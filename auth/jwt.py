from jose import jwt, JWTError
from core.config import data
from datetime import datetime, timezone, timedelta


class JWT:
    ACCESS_TOKEN_EXPIRE_HOURS = 12

    def secret(self) -> str:
        secret = data().secret()

        if not secret or len(secret) < 32:
            raise RuntimeError("SECRET precisa ter pelo menos 32 caracteres.")

        return secret

    def token(self, email: str, user_id: int, status: bool, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "email": email,
            "status": status,
            "role": role,
            "iat": now,
            "exp": now + timedelta(hours=self.ACCESS_TOKEN_EXPIRE_HOURS),
        }

        return jwt.encode(payload, self.secret(), algorithm="HS256")

    def get_jwt(self, key: str, token: str):
        if key not in ["user_id", "email", "role", "status"]:
            raise ValueError(f"{key} is invalid")

        try:
            payload = jwt.decode(
                token,
                self.secret(),
                algorithms=["HS256"],
                options={"require_exp": True},
            )
            return payload.get(key)

        except JWTError:
            return None

    def decode(self, token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                self.secret(),
                algorithms=["HS256"],
                options={"require_exp": True},
            )
        except JWTError:
            return None
        
    def token_password_change(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "type": "password_change",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
        }

        return jwt.encode(
            payload,
            self.secret(),
            algorithm="HS256"
        )

    def validate_password_change_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.secret(),
                algorithms=["HS256"]
            )

            if payload.get("type") != "password_change":
                return {"valid": False}

            return {
                "valid": True,
                "user_id": payload["user_id"]
            }

        except JWTError:
            return {"valid": False}
