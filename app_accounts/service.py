from app_accounts.repository import RepositoryAccount
from auth.jwt import JWT
from auth.manager_auth import valid_jwt
from auth.dependences import Valid
from auth.hash import hash3
class Service:
    def __init__(self)->None:
        self.app = RepositoryAccount()
        self.jwt = JWT()
        self.valid = Valid
        self.hash = hash3()
    
    def create_account(self, name:str, email:str, password:str) -> bool:
        if self.app.select_by_email(email)is not None:
            return False
        Pass = self.hash.encoder_bcr(password)
        self.app.create(email=email, name=name, password=Pass, status=False, role="user")
        return True
        
        
        
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
            
                
            if (datetime.now()> code_user[-1] > timedelta(minutes=10)) or (code_user == code):
                    session.execute(text("DELETE FROM validation WHERE user_id = :user_id"), {"user_id": id})
                    
            return {"status":True if code_user == code else False,"expired": True if (datetime.now()> code_user[-1] > timedelta(minutes=10)) else False}
                
            
            
        
    def valid_createAccount_code(self, email:str, code:int) -> dict:
        from sqlalchemy import text
        from connect.manager_database import main_database
        from datetime import datetime, timedelta

        app = main_database()

        with app.connect() as session:
            result = session.execute(
                text("""
                    SELECT validation_id, email, number, used, created_at
                    FROM validation_account
                    WHERE email = :email
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"email": email}
            )

            row = result.fetchone()

            if not row:
                return {"status": False, "expired": False}

            data = dict(row._mapping)

            expired = datetime.now() > data["created_at"] + timedelta(minutes=10)
            status = str(data["number"]) == str(code)

            if expired:
                session.execute(
                    text("""
                        DELETE FROM validation_account
                        WHERE validation_id = :validation_id
                    """),
                    {"validation_id": data["validation_id"]}
                )
                session.commit()

                return {"status": False, "expired": True}

            if data["used"]:
                return {"status": False, "expired": False}

            if status:
                session.execute(
                    text("""
                        UPDATE validation_account
                        SET used = true
                        WHERE validation_id = :validation_id
                    """),
                    {"validation_id": data["validation_id"]}
                )
                session.commit()

            return {
                "status": status,
                "expired": expired
            }
            
        
        
        
                
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
      
    
        
        
        
    
        
    
    