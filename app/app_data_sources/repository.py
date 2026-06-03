from datetime import date, datetime
import json
import math

import pandas as pd
from sqlalchemy import text

from connect.manager_database import main_database


engine = main_database()


class RepositoryDataSources:
    def __init__(self) -> None:
        self.db = engine

    def _make_json_safe(self, value):
        if isinstance(value, dict):
            return {
                str(key): self._make_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._make_json_safe(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                self._make_json_safe(item)
                for item in value
            ]

        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None

        if pd.isna(value) if not isinstance(value, (list, dict, tuple, str)) else False:
            return None

        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:
                return value

        return value

    def _json_dumps(self, value) -> str:
        return json.dumps(
            self._make_json_safe(value),
            ensure_ascii=False,
            default=str
        )

    def _row_to_dict(self, row) -> dict | None:
        return dict(row._mapping) if row else None

    def create_data_source(
        self,
        user_id: int,
        name: str,
        file_name: str,
        file_data: list[dict],
        row_count: int,
        column_count: int,
        source_type: str = "file",
        connection_config: dict | None = None,
        refresh_interval_days: int | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO data_sources (
                        user_id,
                        name,
                        file_name,
                        file_data,
                        row_count,
                        column_count,
                        source_type,
                        connection_config,
                        refresh_interval_days,
                        last_synced_at,
                        next_sync_at
                    )
                    VALUES (
                        :user_id,
                        :name,
                        :file_name,
                        CAST(:file_data AS JSONB),
                        :row_count,
                        :column_count,
                        :source_type,
                        CAST(:connection_config AS JSONB),
                        :refresh_interval_days,
                        NOW(),
                        CASE
                            WHEN :refresh_interval_days IS NULL THEN NULL
                            ELSE NOW() + (:refresh_interval_days || ' days')::interval
                        END
                    )
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "file_name": file_name,
                    "file_data": self._json_dumps(file_data),
                    "row_count": row_count,
                    "column_count": column_count,
                    "source_type": source_type,
                    "connection_config": self._json_dumps(connection_config or {}),
                    "refresh_interval_days": refresh_interval_days,
                }
            )

            session.commit()
            data_source = result.fetchone()

        return self._row_to_dict(data_source)

    def select_data_sources_by_user(
        self,
        user_id: int
    ) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT
                        id,
                        user_id,
                        name,
                        file_name,
                        source_type,
                        connection_config,
                        refresh_interval_days,
                        last_synced_at,
                        next_sync_at,
                        row_count,
                        column_count,
                        created_at,
                        updated_at
                    FROM data_sources
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                """),
                {"user_id": user_id}
            )

            data_sources = result.fetchall()

        return [
            dict(data_source._mapping)
            for data_source in data_sources
        ]

    def select_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM data_sources
                    WHERE id = :data_source_id
                    AND user_id = :user_id
                """),
                {
                    "data_source_id": data_source_id,
                    "user_id": user_id,
                }
            )

            data_source = result.fetchone()

        return self._row_to_dict(data_source)

    def update_data_source(
        self,
        user_id: int,
        data_source_id: int,
        file_name: str,
        file_data: list[dict],
        row_count: int,
        column_count: int,
        source_type: str | None = None,
        connection_config: dict | None = None,
        refresh_interval_days: int | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE data_sources
                    SET
                        file_name = :file_name,
                        file_data = CAST(:file_data AS JSONB),
                        row_count = :row_count,
                        column_count = :column_count,
                        source_type = COALESCE(:source_type, source_type),
                        connection_config = COALESCE(CAST(:connection_config AS JSONB), connection_config),
                        refresh_interval_days = :refresh_interval_days,
                        last_synced_at = NOW(),
                        next_sync_at = CASE
                            WHEN :refresh_interval_days IS NULL THEN NULL
                            ELSE NOW() + (:refresh_interval_days || ' days')::interval
                        END,
                        updated_at = NOW()
                    WHERE id = :data_source_id
                    AND user_id = :user_id
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "data_source_id": data_source_id,
                    "file_name": file_name,
                    "file_data": self._json_dumps(file_data),
                    "row_count": row_count,
                    "column_count": column_count,
                    "source_type": source_type,
                    "connection_config": self._json_dumps(connection_config) if connection_config is not None else None,
                    "refresh_interval_days": refresh_interval_days,
                }
            )

            session.commit()
            data_source = result.fetchone()

        return self._row_to_dict(data_source)

    def select_due_data_sources_by_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM data_sources
                    WHERE user_id = :user_id
                    AND source_type IN ('web', 'database')
                    AND refresh_interval_days IS NOT NULL
                    AND next_sync_at IS NOT NULL
                    AND next_sync_at <= NOW()
                    ORDER BY next_sync_at ASC
                """),
                {"user_id": user_id}
            )

            rows = result.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def rename_data_source(
        self,
        user_id: int,
        data_source_id: int,
        name: str
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE data_sources
                    SET
                        name = :name,
                        updated_at = NOW()
                    WHERE id = :data_source_id
                    AND user_id = :user_id
                    RETURNING
                        id,
                        user_id,
                        name,
                        file_name,
                        row_count,
                        column_count,
                        created_at,
                        updated_at
                """),
                {
                    "user_id": user_id,
                    "data_source_id": data_source_id,
                    "name": name,
                }
            )

            session.commit()
            data_source = result.fetchone()

        return self._row_to_dict(data_source)

    def delete_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM data_sources
                    WHERE id = :data_source_id
                    AND user_id = :user_id
                """),
                {
                    "data_source_id": data_source_id,
                    "user_id": user_id,
                }
            )

            session.commit()

        return result.rowcount > 0

    def delete_all_by_user(
        self,
        user_id: int
    ) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM data_sources
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            session.commit()

        return result.rowcount >= 0
