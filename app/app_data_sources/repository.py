from sqlalchemy import text
from connect.manager_database import main_database
import json

engine = main_database()


class RepositoryDataSources:
    def __init__(self) -> None:
        self.db = engine

    def create_data_source(
        self,
        user_id: int,
        name: str,
        file_name: str,
        file_data: list[dict],
        row_count: int,
        column_count: int
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
                        column_count
                    )
                    VALUES (
                        :user_id,
                        :name,
                        :file_name,
                        CAST(:file_data AS JSONB),
                        :row_count,
                        :column_count
                    )
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "file_name": file_name,
                    "file_data": json.dumps(file_data, ensure_ascii=False),
                    "row_count": row_count,
                    "column_count": column_count
                }
            )

            session.commit()
            data_source = result.fetchone()

        return dict(data_source._mapping) if data_source else None

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
                    "user_id": user_id
                }
            )

            data_source = result.fetchone()

        return dict(data_source._mapping) if data_source else None

    def update_data_source(
        self,
        user_id: int,
        data_source_id: int,
        file_name: str,
        file_data: list[dict],
        row_count: int,
        column_count: int
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
                        updated_at = NOW()
                    WHERE id = :data_source_id
                    AND user_id = :user_id
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "data_source_id": data_source_id,
                    "file_name": file_name,
                    "file_data": json.dumps(file_data, ensure_ascii=False),
                    "row_count": row_count,
                    "column_count": column_count
                }
            )

            session.commit()
            data_source = result.fetchone()

        return dict(data_source._mapping) if data_source else None

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
                    "name": name
                }
            )

            session.commit()
            data_source = result.fetchone()

        return dict(data_source._mapping) if data_source else None

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
                    "user_id": user_id
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