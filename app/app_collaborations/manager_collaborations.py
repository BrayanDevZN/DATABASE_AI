from sqlalchemy import text

from connect.manager_database import main_database


class ManagerCollaborations:
    def __init__(self) -> None:
        self.db = main_database()

    def search_users(self, user_id: int, query: str) -> list[dict]:
        clean_query = query.strip().lstrip("@")
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT user_id, name, username, profile_image
                    FROM users
                    WHERE user_id <> :user_id
                    AND (username ILIKE :query OR name ILIKE :query)
                    ORDER BY
                        CASE WHEN LOWER(username) = LOWER(:exact_query) THEN 0 ELSE 1 END,
                        CASE WHEN LOWER(name) = LOWER(:exact_query) THEN 0 ELSE 1 END,
                        username
                    LIMIT 8
                """),
                {
                    "user_id": user_id,
                    "query": f"%{clean_query}%",
                    "exact_query": clean_query,
                }
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def select_dashboard_access(self, user_id: int, dashboard_id: int) -> dict | None:
        with self.db.connect() as session:
            row = session.execute(
                text("""
                    SELECT d.*, dc.id AS collaboration_id, u.name AS creator_name, u.username AS creator_username,
                        u.profile_image AS creator_profile_image,
                        CASE WHEN d.user_id = :user_id THEN 'owner' ELSE dc.permission END AS access_permission,
                        (d.user_id <> :user_id) AS is_shared
                    FROM dashboards d
                    JOIN users u ON u.user_id = d.user_id
                    LEFT JOIN dashboard_collaborations dc
                        ON dc.dashboard_id = d.id AND dc.collaborator_user_id = :user_id
                        AND dc.status = 'accepted'
                    WHERE d.id = :dashboard_id
                    AND (d.user_id = :user_id OR dc.id IS NOT NULL)
                """),
                {"user_id": user_id, "dashboard_id": dashboard_id}
            ).fetchone()
        return dict(row._mapping) if row else None

    def select_shared_dashboards(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT d.*, dc.id AS collaboration_id, dc.permission AS access_permission, TRUE AS is_shared,
                        u.name AS creator_name, u.username AS creator_username,
                        u.profile_image AS creator_profile_image
                    FROM dashboard_collaborations dc
                    JOIN dashboards d ON d.id = dc.dashboard_id
                    JOIN users u ON u.user_id = d.user_id
                    WHERE dc.collaborator_user_id = :user_id AND dc.status = 'accepted'
                    ORDER BY dc.updated_at DESC
                """),
                {"user_id": user_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def select_shared_data_sources(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT DISTINCT ON (ds.id) ds.id, ds.user_id, ds.name, ds.file_name,
                        ds.row_count, ds.column_count, ds.created_at, ds.updated_at,
                        TRUE AS is_shared, u.username AS creator_username,
                        u.profile_image AS creator_profile_image
                    FROM dashboard_collaborations dc
                    JOIN dashboards d ON d.id = dc.dashboard_id
                    JOIN data_sources ds ON ds.id = d.data_source_id
                    JOIN users u ON u.user_id = ds.user_id
                    WHERE dc.collaborator_user_id = :user_id AND dc.permission = 'full'
                    AND dc.status = 'accepted'
                    ORDER BY ds.id, ds.updated_at DESC
                """),
                {"user_id": user_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def select_data_source_access(self, user_id: int, data_source_id: int) -> dict | None:
        with self.db.connect() as session:
            row = session.execute(
                text("""
                    SELECT ds.user_id AS owner_user_id,
                        CASE WHEN ds.user_id = :user_id THEN 'owner' ELSE 'full' END AS access_permission
                    FROM data_sources ds
                    WHERE ds.id = :data_source_id AND (
                        ds.user_id = :user_id OR EXISTS (
                            SELECT 1 FROM dashboard_collaborations dc
                            JOIN dashboards d ON d.id = dc.dashboard_id
                            WHERE d.data_source_id = ds.id
                            AND dc.collaborator_user_id = :user_id AND dc.permission = 'full'
                            AND dc.status = 'accepted'
                        )
                    )
                """),
                {"user_id": user_id, "data_source_id": data_source_id}
            ).fetchone()
        return dict(row._mapping) if row else None

    def list_dashboard_collaborations(self, user_id: int, dashboard_id: int) -> list[dict]:
        access = self.select_dashboard_access(user_id, dashboard_id)
        if not access or access["access_permission"] != "owner":
            raise ValueError("Apenas o criador pode gerenciar colaboradores.")
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT dc.id, dc.dashboard_id, dc.permission, dc.created_at, dc.updated_at,
                        dc.status, u.user_id, u.name, u.username, u.profile_image
                    FROM dashboard_collaborations dc
                    JOIN users u ON u.user_id = dc.collaborator_user_id
                    WHERE dc.dashboard_id = :dashboard_id ORDER BY dc.status, u.username
                """),
                {"dashboard_id": dashboard_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def share_dashboard(self, user_id: int, dashboard_id: int, username: str, permission: str) -> dict:
        access = self.select_dashboard_access(user_id, dashboard_id)
        if not access or access["access_permission"] != "owner":
            raise ValueError("Apenas o criador pode compartilhar este dashboard.")
        with self.db.connect() as session:
            collaborator = session.execute(
                text("SELECT user_id FROM users WHERE LOWER(username) = LOWER(:username)"),
                {"username": username.strip()}
            ).fetchone()
            if not collaborator:
                raise ValueError("Usuario nao encontrado.")
            if collaborator.user_id == user_id:
                raise ValueError("Voce ja e o criador deste dashboard.")
            row = session.execute(
                text("""
                    INSERT INTO dashboard_collaborations
                        (dashboard_id, owner_user_id, collaborator_user_id, permission, status, updated_at)
                    VALUES (:dashboard_id, :owner_user_id, :collaborator_user_id, :permission, 'pending', NOW())
                    ON CONFLICT (dashboard_id, collaborator_user_id)
                    DO UPDATE SET permission = EXCLUDED.permission, status = 'pending', updated_at = NOW()
                    RETURNING *
                """),
                {"dashboard_id": dashboard_id, "owner_user_id": user_id,
                 "collaborator_user_id": collaborator.user_id, "permission": permission}
            ).fetchone()
            session.execute(
                text("""
                    INSERT INTO collaboration_notifications
                        (user_id, collaboration_id, message, notification_type)
                    VALUES (:user_id, :collaboration_id, :message, 'invitation')
                """),
                {
                    "user_id": collaborator.user_id,
                    "collaboration_id": row.id,
                    "message": f"@{access['creator_username']} convidou voce para colaborar em {access['title']}.",
                }
            )
            session.commit()
        return dict(row._mapping)

    def update_collaboration(self, user_id: int, collaboration_id: int, permission: str) -> dict:
        with self.db.connect() as session:
            row = session.execute(
                text("""
                    UPDATE dashboard_collaborations SET permission = :permission, updated_at = NOW()
                    WHERE id = :collaboration_id AND owner_user_id = :user_id RETURNING *
                """),
                {"user_id": user_id, "collaboration_id": collaboration_id, "permission": permission}
            ).fetchone()
            session.commit()
        if not row:
            raise ValueError("Colaboracao nao encontrada.")
        return dict(row._mapping)

    def delete_collaboration(self, user_id: int, collaboration_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM dashboard_collaborations
                    WHERE id = :id
                    AND (owner_user_id = :user_id OR collaborator_user_id = :user_id)
                """),
                {"id": collaboration_id, "user_id": user_id}
            )
            session.commit()
        return result.rowcount > 0

    def select_invitations(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT dc.id, dc.dashboard_id, dc.permission, dc.status, dc.created_at,
                        d.title, u.name AS creator_name, u.username AS creator_username,
                        u.profile_image AS creator_profile_image
                    FROM dashboard_collaborations dc
                    JOIN dashboards d ON d.id = dc.dashboard_id
                    JOIN users u ON u.user_id = dc.owner_user_id
                    WHERE dc.collaborator_user_id = :user_id AND dc.status = 'pending'
                    ORDER BY dc.created_at DESC
                """),
                {"user_id": user_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def respond_invitation(self, user_id: int, collaboration_id: int, response: str) -> dict:
        with self.db.connect() as session:
            row = session.execute(
                text("""
                    UPDATE dashboard_collaborations dc
                    SET status = :response, updated_at = NOW()
                    FROM dashboards d, users u
                    WHERE dc.id = :collaboration_id
                    AND dc.collaborator_user_id = :user_id
                    AND dc.status = 'pending'
                    AND d.id = dc.dashboard_id
                    AND u.user_id = dc.collaborator_user_id
                    RETURNING dc.*, d.title, u.username
                """),
                {"user_id": user_id, "collaboration_id": collaboration_id, "response": response}
            ).fetchone()
            if not row:
                raise ValueError("Convite nao encontrado.")
            verb = "aceitou" if response == "accepted" else "recusou"
            session.execute(
                text("""
                    INSERT INTO collaboration_notifications
                        (user_id, collaboration_id, message, notification_type)
                    VALUES (:user_id, :collaboration_id, :message, :notification_type)
                """),
                {
                    "user_id": row.owner_user_id,
                    "collaboration_id": row.id,
                    "message": f"@{row.username} {verb} o convite para {row.title}.",
                    "notification_type": response,
                }
            )
            session.commit()
        return dict(row._mapping)

    def select_notifications(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT cn.id, cn.collaboration_id, dc.dashboard_id,
                        cn.message, cn.notification_type, cn.is_read, cn.created_at
                    FROM collaboration_notifications cn
                    LEFT JOIN dashboard_collaborations dc ON dc.id = cn.collaboration_id
                    WHERE cn.user_id = :user_id
                    ORDER BY cn.created_at DESC
                    LIMIT 30
                """),
                {"user_id": user_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]

    def mark_notification_read(self, user_id: int, notification_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE collaboration_notifications SET is_read = TRUE
                    WHERE id = :notification_id AND user_id = :user_id
                """),
                {"user_id": user_id, "notification_id": notification_id}
            )
            session.commit()
        return result.rowcount > 0

    def list_dashboard_access(self, user_id: int, dashboard_id: int) -> list[dict]:
        access = self.select_dashboard_access(user_id, dashboard_id)
        if not access:
            raise ValueError("Dashboard nao encontrado ou sem permissao.")
        with self.db.connect() as session:
            rows = session.execute(
                text("""
                    SELECT NULL::INTEGER AS id, 'owner' AS permission, 'accepted' AS status,
                        u.user_id, u.name, u.username, u.profile_image
                    FROM dashboards d
                    JOIN users u ON u.user_id = d.user_id
                    WHERE d.id = :dashboard_id
                    UNION ALL
                    SELECT dc.id, dc.permission, dc.status, u.user_id, u.name, u.username, u.profile_image
                    FROM dashboard_collaborations dc
                    JOIN users u ON u.user_id = dc.collaborator_user_id
                    WHERE dc.dashboard_id = :dashboard_id AND dc.status = 'accepted'
                    ORDER BY username
                """),
                {"dashboard_id": dashboard_id}
            ).fetchall()
        return [dict(row._mapping) for row in rows]
