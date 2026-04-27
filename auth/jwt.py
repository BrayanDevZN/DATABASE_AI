
from jose import jwt, JWTError
from core.config import data

class JWT:
   
        
    def token(self, email:str, user_id:int, status:str, role:str) -> str:
        payload = {
            "user_id":user_id,
            "email":email, 
            "role":status,
            "role":role
        }
        
        return jwt.encode(payload, data().secret(), algorithm="HS256")
    
    
    def get_jwt(self, data:str, token:bytes) -> bool | None:
        
        if not data in ["user_id", "email", "role", "status"]:
            raise ValueError(f"{data} is invalid")
        
        try:
            payload = jwt.decode(
                token,
                data().secret(),
                algorithms=["HS256"]
            )
            
            return payload.get(data)

        except JWTError:
            return None
        
    def decode(self, token:bytes) ->dict:
            try:
                payload = jwt.decode(
                    token,
                    data().secret(),
                    algorithms=["HS256"]
                )

                return payload
            except JWTError:
                return None
            
        