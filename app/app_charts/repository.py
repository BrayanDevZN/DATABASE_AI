from sqlalchemy import text
from connect.manager_database import main_database
import json

engine = main_database()


class RepositoryCharts:
    def __init__(self) -> None:
        self.db = engine

    def create_dashboard(
        self,
        user_id: int,
        title: str,
        prompt: str,
        ai_suggestion: str | None,
        file_name: str | None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboards (
                        user_id,
                        title,
                        prompt,
                        ai_suggestion,
                        file_name
                    )
                    VALUES (
                        :user_id,
                        :title,
                        :prompt,
                        :ai_suggestion,
                        :file_name
                    )
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "title": title,
                    "prompt": prompt,
                    "ai_suggestion": ai_suggestion,
                    "file_name": file_name
                }
            )

            session.commit()
            dashboard = result.fetchone()

        return dict(dashboard._mapping) if dashboard else None

    def create_chart(
        self,
        dashboard_id: int,
        chart_type: str,
        title: str,
        chart_data: dict,
        chart_config: dict | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboard_charts (
                        dashboard_id,
                        chart_type,
                        title,
                        chart_data,
                        chart_config
                    )
                    VALUES (
                        :dashboard_id,
                        :chart_type,
                        :title,
                        CAST(:chart_data AS JSONB),
                        CAST(:chart_config AS JSONB)
                    )
                    RETURNING *
                """),
                {
                    "dashboard_id": dashboard_id,
                    "chart_type": chart_type,
                    "title": title,
                    "chart_data": json.dumps(chart_data, ensure_ascii=False),
                    "chart_config": json.dumps(chart_config or {}, ensure_ascii=False)
                }
            )

            session.commit()
            chart = result.fetchone()

        return dict(chart._mapping) if chart else None

    def select_dashboards_by_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                """),
                {"user_id": user_id}
            )

            dashboards = result.fetchall()

        return [dict(dashboard._mapping) for dashboard in dashboards]

    def select_dashboard(self, user_id: int, dashboard_id: int) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE id = :dashboard_id
                    AND user_id = :user_id
                """),
                {
                    "dashboard_id": dashboard_id,
                    "user_id": user_id
                }
            )

            dashboard = result.fetchone()

        return dict(dashboard._mapping) if dashboard else None

    def select_charts_by_dashboard(self, dashboard_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboard_charts
                    WHERE dashboard_id = :dashboard_id
                    ORDER BY created_at ASC
                """),
                {"dashboard_id": dashboard_id}
            )

            charts = result.fetchall()

        return [dict(chart._mapping) for chart in charts]

    def delete_dashboard(self, user_id: int, dashboard_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM dashboards
                    WHERE id = :dashboard_id
                    AND user_id = :user_id
                """),
                {
                    "dashboard_id": dashboard_id,
                    "user_id": user_id
                }
            )

            session.commit()

        return result.rowcount > 0

    def delete_all_by_user(self, user_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM dashboards
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            session.commit()

        return result.rowcount >= 0

    def save_chart_settings(
        self,
        dashboard_id: int,
        chart_id: int | None,
        chart_color: str,
        chart_background: str,
        x_axis_text_color: str,
        y_axis_text_color: str,
        grid_color: str,
        grid_style: str,
        bar_style: str
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboard_chart_settings (
                        dashboard_id,
                        chart_id,
                        chart_color,
                        chart_background,
                        x_axis_text_color,
                        y_axis_text_color,
                        grid_color,
                        grid_style,
                        bar_style,
                        updated_at
                    )
                    VALUES (
                        :dashboard_id,
                        :chart_id,
                        :chart_color,
                        :chart_background,
                        :x_axis_text_color,
                        :y_axis_text_color,
                        :grid_color,
                        :grid_style,
                        :bar_style,
                        NOW()
                    )
                    ON CONFLICT (chart_id)
                    DO UPDATE SET
                        chart_color = EXCLUDED.chart_color,
                        chart_background = EXCLUDED.chart_background,
                        x_axis_text_color = EXCLUDED.x_axis_text_color,
                        y_axis_text_color = EXCLUDED.y_axis_text_color,
                        grid_color = EXCLUDED.grid_color,
                        grid_style = EXCLUDED.grid_style,
                        bar_style = EXCLUDED.bar_style,
                        updated_at = NOW()
                    RETURNING *
                """),
                {
                    "dashboard_id": dashboard_id,
                    "chart_id": chart_id,
                    "chart_color": chart_color,
                    "chart_background": chart_background,
                    "x_axis_text_color": x_axis_text_color,
                    "y_axis_text_color": y_axis_text_color,
                    "grid_color": grid_color,
                    "grid_style": grid_style,
                    "bar_style": bar_style
                }
            )

            session.commit()
            settings = result.fetchone()

        return dict(settings._mapping) if settings else None

    def select_chart_settings(
        self,
        dashboard_id: int,
        chart_id: int | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            if chart_id:
                result = session.execute(
                    text("""
                        SELECT *
                        FROM dashboard_chart_settings
                        WHERE dashboard_id = :dashboard_id
                        AND chart_id = :chart_id
                    """),
                    {
                        "dashboard_id": dashboard_id,
                        "chart_id": chart_id
                    }
                )
            else:
                result = session.execute(
                    text("""
                        SELECT *
                        FROM dashboard_chart_settings
                        WHERE dashboard_id = :dashboard_id
                        AND chart_id IS NULL
                    """),
                    {"dashboard_id": dashboard_id}
                )

            settings = result.fetchone()

        return dict(settings._mapping) if settings else None