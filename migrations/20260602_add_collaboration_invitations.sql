ALTER TABLE dashboard_collaborations
ADD COLUMN IF NOT EXISTS status VARCHAR(10) NOT NULL DEFAULT 'accepted'
CHECK (status IN ('pending', 'accepted', 'declined'));

CREATE TABLE IF NOT EXISTS collaboration_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    collaboration_id INTEGER REFERENCES dashboard_collaborations(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(20) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS collaboration_notifications_user_idx
ON collaboration_notifications (user_id, created_at DESC);

ALTER TABLE collaboration_notifications
DROP CONSTRAINT IF EXISTS collaboration_notifications_collaboration_id_fkey;

ALTER TABLE collaboration_notifications
ADD CONSTRAINT collaboration_notifications_collaboration_id_fkey
FOREIGN KEY (collaboration_id) REFERENCES dashboard_collaborations(id) ON DELETE SET NULL;
