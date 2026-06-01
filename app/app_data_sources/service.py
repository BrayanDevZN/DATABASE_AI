from app.app_data_sources.repository import RepositoryDataSources


class ServiceDataSources:
    def __init__(self) -> None:
        self.repo = RepositoryDataSources()

    def create_data_source(
        self,
        user_id: int,
        name: str,
        file_name: str,
        file_data: list[dict],
        row_count: int,
        column_count: int
    ) -> dict | None:
        return self.repo.create_data_source(
            user_id=user_id,
            name=name,
            file_name=file_name,
            file_data=file_data,
            row_count=row_count,
            column_count=column_count
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
        column_count: int
    ) -> dict | None:
        return self.repo.update_data_source(
            user_id=user_id,
            data_source_id=data_source_id,
            file_name=file_name,
            file_data=file_data,
            row_count=row_count,
            column_count=column_count
        )

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