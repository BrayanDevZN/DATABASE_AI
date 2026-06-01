import io
import pandas as pd

from fastapi import FastAPI, File, Form, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

import api.model.model_accounts as models
import api.model.model_conversation as conversation_models
import api.model.model_charts as chart_models
import api.model.model_data_source as data_source_models

import app.app_accounts.manager_accounts as manager
import app.app_conversations.manager_conversation as conversation_manager
import app.app_charts.manager_charts as charts_manager
import app.app_data_sources.manager_data_sources as data_source_manager

from auth.jwt import JWT


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_uploaded_file(file: UploadFile) -> tuple[list[dict], int, int]:
    content = file.file.read()
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(content))

    elif filename.endswith(".json"):
        df = pd.read_json(io.BytesIO(content))

    else:
        raise ValueError("Formato inválido. Envie CSV, XLSX, XLS ou JSON.")

    df = df.dropna(how="all")
    df = df.where(pd.notnull(df), None)

    file_data = df.to_dict(orient="records")
    row_count = len(df)
    column_count = len(df.columns)

    return file_data, row_count, column_count


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(data: models.CreateUser):
    return manager.create_User().create(data.model_dump())


@app.post("/env_code_create", status_code=status.HTTP_201_CREATED)
def env_code_create(data: models.ValidEmail):
    return manager.create_User().env_code(data.model_dump())


@app.post("/valid_user", status_code=status.HTTP_200_OK)
def valid_user(data: models.ValidEmail):
    return manager.create_User().valid_user(data.model_dump())


@app.post("/login", status_code=status.HTTP_200_OK)
def login(data: models.Login):
    return manager.User_Login().login(data.model_dump())


@app.post("/env_pass", status_code=status.HTTP_200_OK)
def env_pass(data: models.Env_CodePass):
    return manager.User_Login().Env_codePass(data=data.model_dump())


@app.patch("/update_auth_pass", status_code=status.HTTP_200_OK)
def update_auth_pass(data: models.UpdateAuthPass):
    return manager.User_Login().updateAuth_Pass(data=data.model_dump())


@app.patch("/update_pass", status_code=status.HTTP_200_OK)
def update_pass(data: models.Pass):
    return manager.User_Login().update_Pass(data.model_dump())


@app.post("/check_pass", status_code=status.HTTP_200_OK)
def check_pass(data: models.Pass):
    return manager.User_Login().check_pass(data.model_dump())


@app.patch("/update_name", status_code=status.HTTP_200_OK)
def update_name(data: models.UpName):
    return manager.User_Login().update_name(data.model_dump())


@app.post("/valid_token", status_code=status.HTTP_200_OK)
def valid_token(data: models.ValidToken):
    return manager.User_Login().valid_token(data.model_dump())


@app.post("/me", status_code=status.HTTP_200_OK)
def me(data: models.ValidToken):
    return manager.User_Login().me(data.model_dump())


@app.post("/conversation", status_code=status.HTTP_201_CREATED)
def create_conversation(data: conversation_models.SaveMessageWithToken):
    return conversation_manager.ManagerConversation().create(data.model_dump())


@app.post("/conversations", status_code=status.HTTP_200_OK)
def select_conversations(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().select_conversations(
        data.model_dump()
    )


@app.post("/conversation/messages", status_code=status.HTTP_200_OK)
def select_by_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().select_by_conversation(
        data.model_dump()
    )


@app.post("/conversation/user", status_code=status.HTTP_200_OK)
def select_by_user(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().select_by_user(
        data.model_dump()
    )


@app.delete("/conversation", status_code=status.HTTP_200_OK)
def delete_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().delete_conversation(
        data.model_dump()
    )


@app.post("/conversation/create", status_code=status.HTTP_201_CREATED)
def create_empty_conversation(data: conversation_models.CreateConversation):
    return conversation_manager.ManagerConversation().create_empty(
        data.model_dump()
    )


# DATA SOURCES

@app.post("/data-source/create", status_code=status.HTTP_201_CREATED)
def create_data_source(
    token: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
):
    user_id = JWT().get_jwt(
        key="user_id",
        token=token
    )

    file_data, row_count, column_count = read_uploaded_file(file)

    data_source = data_source_manager.ManagerDataSources().create_data_source(
        user_id=user_id,
        name=name,
        file_name=file.filename,
        file_data=file_data,
        row_count=row_count,
        column_count=column_count
    )

    return {
        "data_source": data_source
    }


@app.post("/data-sources", status_code=status.HTTP_200_OK)
def select_data_sources(data: data_source_models.WithToken):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    return {
        "data_sources": data_source_manager.ManagerDataSources()
        .select_data_sources_by_user(user_id=user_id)
    }


@app.post("/data-source", status_code=status.HTTP_200_OK)
def select_data_source(data: data_source_models.GetDataSource):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    data_source = data_source_manager.ManagerDataSources().select_data_source(
        user_id=user_id,
        data_source_id=data.data_source_id
    )

    return {
        "data_source": data_source
    }


@app.patch("/data-source/update", status_code=status.HTTP_200_OK)
def update_data_source(
    token: str = Form(...),
    data_source_id: int = Form(...),
    file: UploadFile = File(...)
):
    user_id = JWT().get_jwt(
        key="user_id",
        token=token
    )

    file_data, row_count, column_count = read_uploaded_file(file)

    data_source = data_source_manager.ManagerDataSources().update_data_source(
        user_id=user_id,
        data_source_id=data_source_id,
        file_name=file.filename,
        file_data=file_data,
        row_count=row_count,
        column_count=column_count
    )

    return {
        "data_source": data_source
    }


@app.patch("/data-source/rename", status_code=status.HTTP_200_OK)
def rename_data_source(data: data_source_models.RenameDataSource):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    data_source = data_source_manager.ManagerDataSources().rename_data_source(
        user_id=user_id,
        data_source_id=data.data_source_id,
        name=data.name
    )

    return {
        "data_source": data_source
    }


@app.delete("/data-source", status_code=status.HTTP_200_OK)
def delete_data_source(data: data_source_models.DeleteDataSource):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    deleted = data_source_manager.ManagerDataSources().delete_data_source(
        user_id=user_id,
        data_source_id=data.data_source_id
    )

    return {
        "status": deleted
    }


# DASHBOARDS

@app.post("/dashboards", status_code=status.HTTP_200_OK)
def select_dashboards(data: chart_models.WithToken):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    return {
        "dashboards": charts_manager.ManagerCharts().select_dashboards_by_user(
            user_id=user_id
        )
    }


@app.post("/dashboard", status_code=status.HTTP_200_OK)
def select_dashboard(data: chart_models.GetDashboard):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    dashboard = charts_manager.ManagerCharts().select_dashboard_with_charts(
        user_id=user_id,
        dashboard_id=data.dashboard_id
    )

    return {
        "dashboard": dashboard
    }


@app.post("/dashboard/create", status_code=status.HTTP_201_CREATED)
def create_dashboard(data: chart_models.CreateDashboard):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    dashboard = charts_manager.ManagerCharts().create_dashboard(
        user_id=user_id,
        title=data.title,
        prompt=data.prompt,
        ai_suggestion=data.ai_suggestion,
        file_name=data.file_name
    )

    return {
        "dashboard": dashboard
    }


@app.post("/dashboard/chart/create", status_code=status.HTTP_201_CREATED)
def create_dashboard_chart(data: chart_models.CreateChart):
    chart = charts_manager.ManagerCharts().create_chart(
        dashboard_id=data.dashboard_id,
        chart_type=data.chart_type,
        title=data.title,
        chart_data=data.chart_data,
        chart_config=data.chart_config
    )

    return {
        "chart": chart
    }


@app.post("/dashboard/chart/settings", status_code=status.HTTP_200_OK)
def save_chart_settings(data: chart_models.SaveChartSettings):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    dashboard = charts_manager.ManagerCharts().select_dashboard_with_charts(
        user_id=user_id,
        dashboard_id=data.dashboard_id
    )

    if not dashboard:
        return {
            "status": False,
            "message": "Dashboard não encontrado ou não pertence ao usuário."
        }

    if data.chart_id:
        chart_ids = [
            chart["id"]
            for chart in dashboard.get("charts", [])
        ]

        if data.chart_id not in chart_ids:
            return {
                "status": False,
                "message": "Gráfico não encontrado ou não pertence ao dashboard."
            }

    settings = charts_manager.ManagerCharts().save_chart_settings(
        dashboard_id=data.dashboard_id,
        chart_id=data.chart_id,
        chart_color=data.chart_color,
        chart_background=data.chart_background,
        x_axis_text_color=data.x_axis_text_color,
        y_axis_text_color=data.y_axis_text_color,
        grid_color=data.grid_color,
        grid_style=data.grid_style,
        bar_style=data.bar_style,
        pie_colors=data.pie_colors,
        show_legend=data.show_legend
    )

    return {
        "status": True,
        "settings": settings
    }


@app.delete("/dashboard", status_code=status.HTTP_200_OK)
def delete_dashboard(data: chart_models.DeleteDashboard):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    deleted = charts_manager.ManagerCharts().delete_dashboard(
        user_id=user_id,
        dashboard_id=data.dashboard_id
    )

    return {
        "status": deleted
    }


@app.delete("/delete_user", status_code=status.HTTP_200_OK)
def delete_user(data: models.DeleteUser):
    user_id = JWT().get_jwt(
        key="user_id",
        token=data.token
    )

    if user_id is not None:
        charts_manager.ManagerCharts().delete_all_by_user(
            user_id=user_id
        )

        data_source_manager.ManagerDataSources().delete_all_by_user(
            user_id=user_id
        )

    return manager.User_Login().delete_user(data.model_dump())