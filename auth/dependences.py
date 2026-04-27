from hash import hash3
from jwt import JWT
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
                data = session.execute(text(f'SELECT * from Users where user_id= :user_id'), {"user_id": data["user_id"]})
                user = data.fetchone()
        role = self.jwt.get_jwt(token=token, data="role")
       
        return True if (self.jwt.get_jwt(token=token, data="role") == "admin") and (user["role"] == role) else False
        
    
    def auth_jwt(self, token:bytes) -> bool:
        data = self.jwt.decode(token)
        with engine.connect() as session:
                data = session.execute(text(f'SELECT * from Users where user_id= :user_id'), {"user_id": data["user_id"]})
                user = data.fetchone()
                       
        
        
        return True if user is not None else False
     

            
    def valid_pass(self, value:str, check_value:bytes) ->bool:
        
            return self.hash.check_pw(
                data=self.hash.encoder_bcr(value),
                new_data=check_value
            )
        