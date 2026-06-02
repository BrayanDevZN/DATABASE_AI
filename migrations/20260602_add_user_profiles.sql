ALTER TABLE users
ADD COLUMN IF NOT EXISTS username VARCHAR(30),
ADD COLUMN IF NOT EXISTS profile_image TEXT;

UPDATE users
SET username = 'user_' || user_id
WHERE username IS NULL OR BTRIM(username) = '';

ALTER TABLE users
ALTER COLUMN username SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_unique
ON users (LOWER(username));
