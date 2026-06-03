import io
import json
import os
from datetime import date, datetime

import pandas as pd
import requests

from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

import api.model.model_accounts as models
import api.model.model_conversation as conversation_models
import api.model.model_charts as chart_models
import api.model.model_data_source as data_source_models
import api.model.model_collaboration as collaboration_models

import app.app_accounts.manager_accounts as manager
import app.app_conversations.manager_conversation as conversation_manager
import app.app_charts.manager_charts as charts_manager
import app.app_data_sources.manager_data_sources as data_source_manager
from app.app_collaborations.manager_collaborations import ManagerCollaborations

from auth.jwt import JWT


app = FastAPI()
collaborations = ManagerCollaborations()
AI_URL = os.getenv("AI_URL", "https://web-production-40ead.up.railway.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_json_safe(value):
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if pd.isna(value) if not isinstance(value, (list, dict, tuple, str)) else False:
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value

    return value


def get_user_id_from_token(token: str) -> int:
    user_id = JWT().get_jwt(key="user_id", token=token)

    if user_id is None:
        raise ValueError("Token inválido.")

    return user_id


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

    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df[column] = df[column].astype(str)

    file_data = make_json_safe(df.to_dict(orient="records"))
    row_count = len(df)
    column_count = len(df.columns)

    return file_data, row_count, column_count


def normalize_rows(rows) -> tuple[list[dict], int, int]:
    if isinstance(rows, dict):
        for key in ("data", "results", "items", "rows", "products", "users"):
            if isinstance(rows.get(key), list):
                rows = rows[key]
                break
        else:
            rows = [rows]

    if not isinstance(rows, list):
        raise ValueError("A fonte precisa retornar uma lista de registros.")

    df = pd.DataFrame(rows)
    df = df.dropna(how="all")
    df = df.where(pd.notnull(df), None)

    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df[column] = df[column].astype(str)

    file_data = make_json_safe(df.to_dict(orient="records"))
    row_count = len(df)
    column_count = len(df.columns)

    return file_data, row_count, column_count


def read_web_source(url: str) -> tuple[list[dict], int, int]:
    if not url or not url.strip():
        raise ValueError("URL da API e obrigatoria.")

    response = requests.get(url.strip(), timeout=30)
    response.raise_for_status()

    return normalize_rows(response.json())


def read_web_payload(api_payload: str | None) -> tuple[list[dict], int, int]:
    if not api_payload or not api_payload.strip():
        raise ValueError("URL da API e obrigatoria.")

    try:
        payload = json.loads(api_payload)
    except json.JSONDecodeError:
        raise ValueError("A resposta da API nao esta em JSON valido.")

    return normalize_rows(payload)


def read_database_source(database_url: str, query: str) -> tuple[list[dict], int, int]:
    if not database_url or not database_url.strip():
        raise ValueError("URL de conexao do banco e obrigatoria.")

    if not query or not query.strip():
        raise ValueError("Query do banco e obrigatoria.")

    clean_query = query.strip()

    if not clean_query.lower().startswith("select"):
        raise ValueError("Use apenas consultas SELECT para fontes de banco.")

    engine = create_engine(database_url.strip(), pool_pre_ping=True)

    with engine.connect() as session:
        rows = session.execute(text(clean_query)).mappings().all()

    return normalize_rows([dict(row) for row in rows])


def normalize_refresh_interval(value: int | str | None) -> int | None:
    if value in (None, ""):
        return None

    days = int(value)

    if days < 1:
        raise ValueError("O limite de atualizacao precisa ser de pelo menos 1 dia.")

    return days


def build_connection_config(
    source_type: str,
    api_url: str | None = None,
    database_url: str | None = None,
    query: str | None = None,
) -> dict:
    if source_type == "web":
        return {"url": (api_url or "").strip()}

    if source_type == "database":
        return {
            "database_url": (database_url or "").strip(),
            "query": (query or "").strip(),
        }

    return {}


def read_source_payload(
    source_type: str,
    file: UploadFile | None = None,
    api_url: str | None = None,
    api_payload: str | None = None,
    database_url: str | None = None,
    query: str | None = None,
) -> tuple[list[dict], int, int, str]:
    if source_type == "file":
        if not file:
            raise ValueError("Arquivo e obrigatorio para fonte do tipo arquivo.")

        file_data, row_count, column_count = read_uploaded_file(file)
        return file_data, row_count, column_count, file.filename

    if source_type == "web":
        if api_payload:
            file_data, row_count, column_count = read_web_payload(api_payload)
        else:
            file_data, row_count, column_count = read_web_source(api_url or "")
        return file_data, row_count, column_count, api_url or "API externa"

    if source_type == "database":
        file_data, row_count, column_count = read_database_source(database_url or "", query or "")
        return file_data, row_count, column_count, "Banco de dados"

    raise ValueError("Tipo de fonte invalido.")


def analyze_dashboard_refresh_with_ai(
    token: str,
    dashboard: dict,
) -> dict:
    form_data = {
        "token": token,
        "title": dashboard.get("title") or "Dashboard",
        "prompt": dashboard.get("prompt") or "",
        "data_source_id": str(dashboard["data_source_id"]),
    }

    response = requests.post(
        f"{AI_URL}/dashboard/refresh/analyze",
        data=form_data,
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def refresh_linked_dashboards_after_source_sync(
    token: str,
    user_id: int,
    source: dict,
    dashboards: list[dict],
) -> list[dict]:
    refreshed_dashboards = []
    chart_manager = charts_manager.ManagerCharts()

    for dashboard in dashboards:
        try:
            analysis = analyze_dashboard_refresh_with_ai(
                token=token,
                dashboard=dashboard,
            )
            charts = (
                analysis.get("charts")
                or analysis.get("dashboard", {}).get("charts")
                or []
            )
            ai_suggestion = (
                analysis.get("ai_suggestion")
                or analysis.get("dashboard", {}).get("ai_suggestion")
                or analysis.get("answer")
                or ""
            )

            if not charts:
                raise ValueError("A IA nao retornou graficos para o dashboard.")

            refreshed_dashboard = chart_manager.finish_dashboard_refresh(
                user_id=user_id,
                dashboard_id=dashboard["id"],
                ai_suggestion=ai_suggestion,
                charts=charts,
                prompt=dashboard.get("prompt"),
            )

            collaborations.notify_dashboard_refreshed(
                owner_user_id=user_id,
                dashboard_id=dashboard["id"],
                dashboard_title=dashboard.get("title") or "Dashboard",
                source_name=source.get("name") or "Fonte de dados",
            )
            refreshed_dashboards.append(refreshed_dashboard)
        except Exception as error:
            chart_manager.mark_dashboards_outdated_by_data_source(
                data_source_id=source["id"],
            )
            collaborations.create_notification(
                user_id=user_id,
                dashboard_id=dashboard.get("id"),
                message=(
                    f'Nao foi possivel atualizar automaticamente o dashboard '
                    f'"{dashboard.get("title", "Dashboard")}" da fonte '
                    f'"{source.get("name", "Fonte de dados")}". Atualize manualmente.'
                ),
                notification_type="dashboard_auto_refresh_failed",
            )
            refreshed_dashboards.append({
                "dashboard": dashboard,
                "error": str(error),
            })

    return refreshed_dashboards


def sync_due_data_sources(user_id: int, token: str) -> list[dict]:
    manager_data_sources = data_source_manager.ManagerDataSources()
    synced = []

    for source in manager_data_sources.select_due_data_sources_by_user(user_id):
        config = source.get("connection_config") or {}
        source_type = source.get("source_type")

        try:
            file_data, row_count, column_count, file_name = read_source_payload(
                source_type=source_type,
                api_url=config.get("url"),
                database_url=config.get("database_url"),
                query=config.get("query"),
            )

            updated_source = manager_data_sources.update_data_source(
                user_id=user_id,
                data_source_id=source["id"],
                file_name=file_name,
                file_data=file_data,
                row_count=row_count,
                column_count=column_count,
                source_type=source_type,
                connection_config=config,
                refresh_interval_days=source.get("refresh_interval_days"),
            )

            dashboards = charts_manager.ManagerCharts().select_dashboards_by_data_source(
                user_id=user_id,
                data_source_id=source["id"],
            )

            refreshed_dashboards = []

            if dashboards:
                refreshed_dashboards = refresh_linked_dashboards_after_source_sync(
                    token=token,
                    user_id=user_id,
                    source=updated_source or source,
                    dashboards=dashboards,
                )

            synced.append({
                "data_source": updated_source,
                "dashboards": dashboards,
                "refreshed_dashboards": refreshed_dashboards,
            })
        except Exception as error:
            synced.append({
                "data_source": source,
                "dashboards": [],
                "error": str(error),
            })

    return synced


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(data: models.CreateUser):
    return manager.create_User().create(data.model_dump())


@app.post("/env_code_create", status_code=status.HTTP_201_CREATED)
def env_code_create(data: models.ValidEmail):
    return manager.create_User().env_code(data.model_dump())


@app.post("/valid_user", status_code=status.HTTP_200_OK)
def valid_user(data: models.ValidEmail):
    return manager.create_User().valid_user(data.model_dump())


@app.post("/valid_username", status_code=status.HTTP_200_OK)
def valid_username(data: models.ValidUsername):
    return manager.create_User().valid_username(data.model_dump())


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


@app.patch("/update_username", status_code=status.HTTP_200_OK)
def update_username(data: models.UpUsername):
    return manager.User_Login().update_username(data.model_dump())


@app.patch("/update_profile_image", status_code=status.HTTP_200_OK)
def update_profile_image(data: models.UpProfileImage):
    return manager.User_Login().update_profile_image(data.model_dump())


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
    return conversation_manager.ManagerConversation().select_conversations(data.model_dump())


@app.post("/conversation/messages", status_code=status.HTTP_200_OK)
def select_by_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().select_by_conversation(data.model_dump())


@app.post("/conversation/user", status_code=status.HTTP_200_OK)
def select_by_user(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().select_by_user(data.model_dump())


@app.delete("/conversation", status_code=status.HTTP_200_OK)
def delete_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().delete_conversation(data.model_dump())


@app.post("/conversation/create", status_code=status.HTTP_201_CREATED)
def create_empty_conversation(data: conversation_models.CreateConversation):
    return conversation_manager.ManagerConversation().create_empty(data.model_dump())


# DATA SOURCES

@app.post("/data-source/create", status_code=status.HTTP_201_CREATED)
def create_data_source(
    token: str = Form(...),
    name: str = Form(...),
    source_type: str = Form("file"),
    refresh_interval_days: int | None = Form(None),
    api_url: str | None = Form(None),
    api_payload: str | None = Form(None),
    database_url: str | None = Form(None),
    query: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    try:
        user_id = get_user_id_from_token(token)
        refresh_interval_days = normalize_refresh_interval(refresh_interval_days)
        file_data, row_count, column_count, file_name = read_source_payload(
            source_type=source_type,
            file=file,
            api_url=api_url,
            api_payload=api_payload,
            database_url=database_url,
            query=query,
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    data_source = data_source_manager.ManagerDataSources().create_data_source(
        user_id=user_id,
        name=name,
        file_name=file_name,
        file_data=file_data,
        row_count=row_count,
        column_count=column_count,
        source_type=source_type,
        connection_config=build_connection_config(
            source_type=source_type,
            api_url=api_url,
            database_url=database_url,
            query=query,
        ),
        refresh_interval_days=refresh_interval_days,
    )

    return {"data_source": data_source}


@app.post("/data-sources", status_code=status.HTTP_200_OK)
def select_data_sources(data: data_source_models.WithToken):
    user_id = get_user_id_from_token(data.token)
    synced_sources = sync_due_data_sources(user_id, data.token)
    owned = data_source_manager.ManagerDataSources().select_data_sources_by_user(user_id=user_id)
    shared = collaborations.select_shared_data_sources(user_id)

    return {
        "data_sources": owned + shared,
        "synced_sources": synced_sources,
        "auto_refresh_dashboards": [
            dashboard
            for synced_source in synced_sources
            for dashboard in synced_source.get("dashboards", [])
        ],
    }


@app.post("/data-source", status_code=status.HTTP_200_OK)
def select_data_source(data: data_source_models.GetDataSource):
    user_id = get_user_id_from_token(data.token)
    access = collaborations.select_data_source_access(user_id, data.data_source_id)
    if not access:
        raise ValueError("Fonte de dados nao encontrada ou sem permissao.")

    data_source = data_source_manager.ManagerDataSources().select_data_source(
        user_id=access["owner_user_id"],
        data_source_id=data.data_source_id,
    )
    if data_source:
        data_source["is_shared"] = access["access_permission"] != "owner"

    return {"data_source": data_source}


@app.post("/data-source/linked-dashboards", status_code=status.HTTP_200_OK)
def select_linked_dashboards(data: data_source_models.GetDataSource):
    user_id = get_user_id_from_token(data.token)
    access = collaborations.select_data_source_access(user_id, data.data_source_id)
    if not access:
        raise ValueError("Fonte de dados nao encontrada ou sem permissao.")

    dashboards = charts_manager.ManagerCharts().select_dashboards_by_data_source(
        user_id=access["owner_user_id"],
        data_source_id=data.data_source_id,
    )
    if access["access_permission"] != "owner":
        dashboards = [
            dashboard for dashboard in dashboards
            if (collaborations.select_dashboard_access(user_id, dashboard["id"]) or {}).get("access_permission") == "full"
        ]

    return {
        "dashboards": dashboards,
        "count": len(dashboards),
    }


@app.patch("/data-source/update", status_code=status.HTTP_200_OK)
def update_data_source(
    token: str = Form(...),
    data_source_id: int = Form(...),
    refresh_dashboards: bool = Form(False),
    source_type: str | None = Form(None),
    refresh_interval_days: int | None = Form(None),
    api_url: str | None = Form(None),
    api_payload: str | None = Form(None),
    database_url: str | None = Form(None),
    query: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    try:
        user_id = get_user_id_from_token(token)
        access = collaborations.select_data_source_access(user_id, data_source_id)
        if not access:
            raise ValueError("Fonte de dados nao encontrada ou sem permissao.")

        linked_dashboards = charts_manager.ManagerCharts().select_dashboards_by_data_source(
            user_id=access["owner_user_id"],
            data_source_id=data_source_id,
        )
        if access["access_permission"] != "owner":
            linked_dashboards = [
                dashboard for dashboard in linked_dashboards
                if (collaborations.select_dashboard_access(user_id, dashboard["id"]) or {}).get("access_permission") == "full"
            ]

        current_source = data_source_manager.ManagerDataSources().select_data_source(
            user_id=access["owner_user_id"],
            data_source_id=data_source_id,
        )

        if not current_source:
            raise ValueError("Fonte de dados nao encontrada.")

        next_source_type = source_type or current_source.get("source_type") or "file"
        current_config = current_source.get("connection_config") or {}
        next_config = build_connection_config(
            source_type=next_source_type,
            api_url=api_url if api_url is not None else current_config.get("url"),
            database_url=database_url if database_url is not None else current_config.get("database_url"),
            query=query if query is not None else current_config.get("query"),
        )
        next_refresh_interval_days = normalize_refresh_interval(refresh_interval_days)

        file_data, row_count, column_count, file_name = read_source_payload(
            source_type=next_source_type,
            file=file,
            api_url=next_config.get("url"),
            api_payload=api_payload,
            database_url=next_config.get("database_url"),
            query=next_config.get("query"),
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    data_source = data_source_manager.ManagerDataSources().update_data_source(
        user_id=access["owner_user_id"],
        data_source_id=data_source_id,
        file_name=file_name,
        file_data=file_data,
        row_count=row_count,
        column_count=column_count,
        source_type=next_source_type,
        connection_config=next_config,
        refresh_interval_days=next_refresh_interval_days,
    )

    if refresh_dashboards and linked_dashboards:
        charts_manager.ManagerCharts().mark_dashboards_outdated_by_data_source(
            data_source_id=data_source_id,
        )

    return {
        "data_source": data_source,
        "linked_dashboards": linked_dashboards,
        "linked_dashboards_count": len(linked_dashboards),
        "refresh_dashboards": refresh_dashboards,
        "dashboards_marked_outdated": bool(refresh_dashboards and linked_dashboards),
        "message": (
            "Fonte atualizada. Dashboards ligados foram marcados para atualização."
            if refresh_dashboards and linked_dashboards
            else "Fonte atualizada."
        ),
    }


@app.patch("/data-source/rename", status_code=status.HTTP_200_OK)
def rename_data_source(data: data_source_models.RenameDataSource):
    user_id = get_user_id_from_token(data.token)
    access = collaborations.select_data_source_access(user_id, data.data_source_id)
    if not access:
        raise ValueError("Fonte de dados nao encontrada ou sem permissao.")

    data_source = data_source_manager.ManagerDataSources().rename_data_source(
        user_id=access["owner_user_id"],
        data_source_id=data.data_source_id,
        name=data.name,
    )

    return {"data_source": data_source}


@app.delete("/data-source", status_code=status.HTTP_200_OK)
def delete_data_source(data: data_source_models.DeleteDataSource):
    user_id = get_user_id_from_token(data.token)

    deleted = data_source_manager.ManagerDataSources().delete_data_source(
        user_id=user_id,
        data_source_id=data.data_source_id,
    )

    return {"status": deleted}


# DASHBOARDS

@app.post("/dashboards", status_code=status.HTTP_200_OK)
def select_dashboards(data: chart_models.WithToken):
    user_id = get_user_id_from_token(data.token)

    return {
        "dashboards": charts_manager.ManagerCharts().select_dashboards_by_user(user_id=user_id),
        "shared_dashboards": collaborations.select_shared_dashboards(user_id),
        "invitations": collaborations.select_invitations(user_id),
    }


@app.post("/dashboard", status_code=status.HTTP_200_OK)
def select_dashboard(data: chart_models.GetDashboard):
    user_id = get_user_id_from_token(data.token)

    dashboard = charts_manager.ManagerCharts().select_dashboard_with_charts(
        user_id=user_id,
        dashboard_id=data.dashboard_id,
    )

    return {"dashboard": dashboard}


@app.post("/dashboard/create", status_code=status.HTTP_201_CREATED)
def create_dashboard(data: chart_models.CreateDashboard):
    user_id = get_user_id_from_token(data.token)

    dashboard = charts_manager.ManagerCharts().create_dashboard(
        user_id=user_id,
        title=data.title,
        prompt=data.prompt,
        ai_suggestion=data.ai_suggestion,
        file_name=data.file_name,
        data_source_id=data.data_source_id,
    )

    return {"dashboard": dashboard}


@app.post("/dashboard/chart/create", status_code=status.HTTP_201_CREATED)
def create_dashboard_chart(data: chart_models.CreateChart):
    chart = charts_manager.ManagerCharts().create_chart(
        dashboard_id=data.dashboard_id,
        chart_type=data.chart_type,
        title=data.title,
        chart_data=data.chart_data,
        chart_config=data.chart_config,
    )

    return {"chart": chart}


@app.post("/dashboard/refresh/finish", status_code=status.HTTP_200_OK)
def finish_dashboard_refresh(data: dict = Body(...)):
    token = data.get("token")
    dashboard_id = data.get("dashboard_id")
    ai_suggestion = data.get("ai_suggestion")
    charts = data.get("charts")
    prompt = data.get("prompt")

    if not token:
        raise ValueError("token é obrigatório.")

    if not dashboard_id:
        raise ValueError("dashboard_id é obrigatório.")

    if ai_suggestion is None:
        raise ValueError("ai_suggestion é obrigatório.")

    if not isinstance(charts, list) or not charts:
        raise ValueError("charts precisa ser uma lista com pelo menos um gráfico.")

    user_id = get_user_id_from_token(token)

    dashboard = charts_manager.ManagerCharts().finish_dashboard_refresh(
        user_id=user_id,
        dashboard_id=int(dashboard_id),
        ai_suggestion=ai_suggestion,
        charts=charts,
        prompt=prompt,
    )

    return {"dashboard": dashboard}


@app.post("/dashboard/chart/settings", status_code=status.HTTP_200_OK)
def save_chart_settings(data: chart_models.SaveChartSettings):
    user_id = get_user_id_from_token(data.token)

    dashboard = charts_manager.ManagerCharts().select_dashboard_with_charts(
        user_id=user_id,
        dashboard_id=data.dashboard_id,
    )

    if not dashboard or dashboard["access_permission"] not in ("owner", "edit", "full"):
        return {
            "status": False,
            "message": "Dashboard não encontrado ou não pertence ao usuário.",
        }

    if data.chart_id:
        chart_ids = [chart["id"] for chart in dashboard.get("charts", [])]

        if data.chart_id not in chart_ids:
            return {
                "status": False,
                "message": "Gráfico não encontrado ou não pertence ao dashboard.",
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
        show_legend=data.show_legend,
    )

    return {
        "status": True,
        "settings": settings,
    }


@app.delete("/dashboard", status_code=status.HTTP_200_OK)
def delete_dashboard(data: chart_models.DeleteDashboard):
    user_id = get_user_id_from_token(data.token)

    deleted = charts_manager.ManagerCharts().delete_dashboard(
        user_id=user_id,
        dashboard_id=data.dashboard_id,
    )

    return {"status": deleted}


# COLLABORATIONS

@app.post("/users/search", status_code=status.HTTP_200_OK)
def search_users(data: collaboration_models.SearchUsers):
    user_id = get_user_id_from_token(data.token)
    return {"users": collaborations.search_users(user_id, data.query)}


@app.post("/collaborations", status_code=status.HTTP_200_OK)
def select_collaboration_overview(data: collaboration_models.WithToken):
    user_id = get_user_id_from_token(data.token)
    return {
        "dashboards": charts_manager.ManagerCharts().select_dashboards_by_user(user_id=user_id),
        "shared_dashboards": collaborations.select_shared_dashboards(user_id),
        "invitations": collaborations.select_invitations(user_id),
    }


@app.post("/dashboard/collaborations", status_code=status.HTTP_200_OK)
def select_dashboard_collaborations(data: collaboration_models.DashboardCollaborations):
    user_id = get_user_id_from_token(data.token)
    return {"collaborators": collaborations.list_dashboard_collaborations(user_id, data.dashboard_id)}


@app.post("/dashboard/collaboration/share", status_code=status.HTTP_201_CREATED)
def share_dashboard(data: collaboration_models.ShareDashboard):
    user_id = get_user_id_from_token(data.token)
    collaboration = collaborations.share_dashboard(
        user_id, data.dashboard_id, data.username, data.permission
    )
    return {"collaboration": collaboration}


@app.patch("/dashboard/collaboration", status_code=status.HTTP_200_OK)
def update_collaboration(data: collaboration_models.UpdateCollaboration):
    user_id = get_user_id_from_token(data.token)
    collaboration = collaborations.update_collaboration(
        user_id, data.collaboration_id, data.permission
    )
    return {"collaboration": collaboration}


@app.delete("/dashboard/collaboration", status_code=status.HTTP_200_OK)
def delete_collaboration(data: collaboration_models.DeleteCollaboration):
    user_id = get_user_id_from_token(data.token)
    return {"status": collaborations.delete_collaboration(user_id, data.collaboration_id)}


@app.post("/dashboard/collaboration/respond", status_code=status.HTTP_200_OK)
def respond_collaboration_invitation(data: collaboration_models.RespondInvitation):
    user_id = get_user_id_from_token(data.token)
    return {
        "collaboration": collaborations.respond_invitation(
            user_id, data.collaboration_id, data.response
        )
    }


@app.post("/dashboard/access", status_code=status.HTTP_200_OK)
def select_dashboard_access_list(data: collaboration_models.DashboardCollaborations):
    user_id = get_user_id_from_token(data.token)
    return {"collaborators": collaborations.list_dashboard_access(user_id, data.dashboard_id)}


@app.post("/notifications", status_code=status.HTTP_200_OK)
def select_notifications(data: collaboration_models.WithToken):
    user_id = get_user_id_from_token(data.token)
    return {"notifications": collaborations.select_notifications(user_id)}


@app.patch("/notification/read", status_code=status.HTTP_200_OK)
def mark_notification_read(data: collaboration_models.MarkNotificationRead):
    user_id = get_user_id_from_token(data.token)
    return {"status": collaborations.mark_notification_read(user_id, data.notification_id)}


@app.delete("/delete_user", status_code=status.HTTP_200_OK)
def delete_user(data: models.DeleteUser):
    user_id = get_user_id_from_token(data.token)

    if user_id is not None:
        charts_manager.ManagerCharts().delete_all_by_user(user_id=user_id)
        data_source_manager.ManagerDataSources().delete_all_by_user(user_id=user_id)

    return manager.User_Login().delete_user(data.model_dump())
