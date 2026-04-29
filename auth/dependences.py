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
        data = self.jwt.decode(token)
        with engine.connect() as session:
                data = session.execute(text(f'SELECT * from users where user_id= :user_id'), {"user_id": data["user_id"]})
                user = data.fetchone()
        role = self.jwt.get_jwt(token=token, key="role")
       
        return True if (self.jwt.get_jwt(token=token, key="role") == "admin") and (user["role"] == role) else False
        
    
    def auth_jwt(self, token:bytes) -> bool:
        data = self.jwt.decode(token)
        with engine.connect() as session:
                data = session.execute(text(f'SELECT * from users where user_id= :user_id'), {"user_id": data["user_id"]})
                user = data.fetchone()
                       
        
        
        return True if user is not None else False
     

            
    def valid_pass(self, value:str, check_value:str) ->bool:
        
       
            return self.hash.check_pw(
                data=value,
                new_data=check_value
            )
        