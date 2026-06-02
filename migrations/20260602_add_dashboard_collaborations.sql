CREATE TABLE IF NOT EXISTS dashboard_collaborations (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
    owner_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    collaborator_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('read', 'edit', 'full')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (dashboard_id, collaborator_user_id),
    CHECK (owner_user_id <> collaborator_user_id)
);

CREATE INDEX IF NOT EXISTS dashboard_collaborations_collaborator_idx
ON dashboard_collaborations (collaborator_user_id);
