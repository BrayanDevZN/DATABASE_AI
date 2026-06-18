from auth.hash import hash3
from auth.jwt import JWT
from connect.manager_database import main_database
from sqlalchemy import  text

engine = main_database()
class Valid:
    def __init__(self) -> None:
        self.hash = hash3()
        self.jwt = JWT()
        
        
    
    
    def auth_admin(self, token:bytes) -> bool:
        payload = self.jwt.decode(token)

        if not payload or "user_id" not in payload:
            return False

        with engine.connect() as session:
                result = session.execute(text('SELECT * from users where user_id= :user_id'), {"user_id": payload["user_id"]})
                user = result.fetchone()

        if user is None:
            return False

        role = self.jwt.get_jwt(token=token, key="role")

        return role == "admin" and user._mapping["role"] == role
        
    
    def auth_jwt(self, token:bytes) -> bool:
        payload = self.jwt.decode(token)

        if not payload or "user_id" not in payload:
            return False

        with engine.connect() as session:
                result = session.execute(text('SELECT * from users where user_id= :user_id'), {"user_id": payload["user_id"]})
                user = result.fetchone()

        return user is not None
     

            
    def valid_pass(self, value:str, check_value:str) ->bool:
        
       
            return self.hash.check_pw(
                data=value,
                new_data=check_value
            )
        
