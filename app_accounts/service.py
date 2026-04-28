from app_accounts.repository import RepositoryAccount
from auth.jwt import JWT
from auth.manager_auth import valid_jwt
from auth.dependences import Valid
class Service:
    def __init__(self)->None:
        self.app = RepositoryAccount()
        self.jwt = JWT()
        self.valid = Valid
        
        
    def update_pass(self, token:str, Pass:str, new_pass:str) ->dict:
        id = self.jwt.get_jwt(key="user_id", token=token)
        user = self.app.select(id)
        password = user["password"]
        check = self.valid.valid_pass(value=Pass, check_value=password)
        check_equal = self.valid.valid_pass(value=new_pass, check_value=password)
        if  check_equal:
            return {"status": "equal"}
        if check:
            self.app.update(user_id=id, password=new_pass)
            return {"status": True}
        
        return {"status":False}
    
    def valid_code(self, token:str, code:str) -> dict:
        from sqlalchemy import text
        from connect.manager_database import main_database
        from datetime import datetime, timedelta
        app = main_database()
        Token = valid_jwt(token).validation()
        if Token["is_valid"]:
            id = self.jwt.get_jwt(key="user_id", token=token)
            with app.connect() as session:
                data =  session.execute(text("SELECT * FROM validation WHERE user_id = :user_id"), {"user_id": id})
                code_user = data.fetchone()
            if code_user == code:
                
                if datetime.now()> code_user[-1] > timedelta(minutes=10):
                    session.execute(text("DELETE FROM validation WHERE user_id = :user_id"), {"user_id": id})
                    return {"status":False,"expired": True}
                return {"status":True, "expired":False}
            
            return  {"status":False, "expired":False}
        
        
                
    def update_AuthPass(self, Pass:str, token:str) -> None:
        id = self.jwt.get_jwt(key="user_id", token=token)
        self.app.update(user_id=id, password=Pass)
        
        
    
    def update_name(self, new_name:str, token:str) -> dict:
          id = self.jwt.get_jwt(key="user_id", token=token)
          user = self.app.select(id)
          
          if user:
              if user["name"] == new_name:
                  return {"status": "equal"}
              
                  
              self.app.update(user_id=id, name=new_name)
              return {"status":True}
          
          return {"status":False}
      
    
        
        
        
    
        
    
    