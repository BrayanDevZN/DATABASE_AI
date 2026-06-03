from app.app_data_sources.service import ServiceDataSources


class ManagerDataSources:
    def __init__(self) -> None:
        self.service = ServiceDataSources()

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
        return self.service.create_data_source(
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
        return self.service.select_data_sources_by_user(
            user_id=user_id
        )

    def select_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> dict | None:
        return self.service.select_data_source(
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
        return self.service.update_data_source(
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
        return self.service.select_due_data_sources_by_user(user_id=user_id)

    def rename_data_source(
        self,
        user_id: int,
        data_source_id: int,
        name: str
    ) -> dict | None:
        return self.service.rename_data_source(
            user_id=user_id,
            data_source_id=data_source_id,
            name=name
        )

    def delete_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> bool:
        return self.service.delete_data_source(
            user_id=user_id,
            data_source_id=data_source_id
        )

    def delete_all_by_user(
        self,
        user_id: int
    ) -> bool:
        return self.service.delete_all_by_user(
            user_id=user_id
        )
