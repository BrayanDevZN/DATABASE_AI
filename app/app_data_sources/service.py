from datetime import date, datetime
import math

from app.app_data_sources.repository import RepositoryDataSources


class ServiceDataSources:
    def __init__(self) -> None:
        self.repo = RepositoryDataSources()

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

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if value is None:
            return None

        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None

        if hasattr(value, "item"):
            try:
                return self._make_json_safe(value.item())
            except Exception:
                return value

        return value

    def _safe_file_data(self, file_data: list[dict]) -> list[dict]:
        if not isinstance(file_data, list):
            return []

        return self._make_json_safe(file_data)

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
        file_data = self._safe_file_data(file_data)

        return self.repo.create_data_source(
            user_id=user_id,
            name=name,
            file_name=file_name,
            file_data=file_data,
            row_count=row_count,
            column_count=column_count,
            source_type=source_type,
            connection_config=connection_config,
            refresh_interval_days=refresh_interval_days
        )

    def select_data_sources_by_user(
        self,
        user_id: int
    ) -> list[dict]:
        return self.repo.select_data_sources_by_user(
            user_id=user_id
        )

    def select_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> dict | None:
        return self.repo.select_data_source(
            user_id=user_id,
            data_source_id=data_source_id
        )

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
        file_data = self._safe_file_data(file_data)

        return self.repo.update_data_source(
            user_id=user_id,
            data_source_id=data_source_id,
            file_name=file_name,
            file_data=file_data,
            row_count=row_count,
            column_count=column_count,
            source_type=source_type,
            connection_config=connection_config,
            refresh_interval_days=refresh_interval_days
        )

    def select_due_data_sources_by_user(self, user_id: int) -> list[dict]:
        return self.repo.select_due_data_sources_by_user(user_id=user_id)

    def rename_data_source(
        self,
        user_id: int,
        data_source_id: int,
        name: str
    ) -> dict | None:
        return self.repo.rename_data_source(
            user_id=user_id,
            data_source_id=data_source_id,
            name=name
        )

    def delete_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> bool:
        return self.repo.delete_data_source(
            user_id=user_id,
            data_source_id=data_source_id
        )

    def delete_all_by_user(
        self,
        user_id: int
    ) -> bool:
        return self.repo.delete_all_by_user(
            user_id=user_id
        )
