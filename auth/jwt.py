from jose import jwt, JWTError
from core.config import data
from datetime import datetime, timezone, timedelta


class JWT:
    def token(self, email: str, user_id: int, status: bool, role: str) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "status": status,
            "role": role
        }

        return jwt.encode(payload, data().secret(), algorithm="HS256")

    def get_jwt(self, key: str, token: str):
        if key not in ["user_id", "email", "role", "status"]:
            raise ValueError(f"{key} is invalid")

        try:
            payload = jwt.decode(
                token,
                data().secret(),
                algorithms=["HS256"]
            )
            return payload.get(key)

        except JWTError:
            return None

    def decode(self, token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                data().secret(),
                algorithms=["HS256"]
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
            data().secret(),
            algorithm="HS256"
        )

    def validate_password_change_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                data().secret(),
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