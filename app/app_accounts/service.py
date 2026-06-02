from app.app_accounts.repository import RepositoryAccount
from auth.jwt import JWT
from auth.manager_auth import valid_jwt
from auth.dependences import Valid
from auth.hash import hash3
class Service:
    def __init__(self)->None:
        self.app = RepositoryAccount()
        self.jwt = JWT()
        self.valid = Valid()
        self.hash = hash3()
    
    def create_account(self, name:str, username:str, email:str, password:str, age:int, gender=str) -> bool:
        if self.app.select_by_email(email) is not None:
            return False
        if self.app.select_by_username(username) is not None:
            return False
        Pass = self.hash.encoder_bcr(password)
        self.app.create(email=email, name=name, username=username, password=Pass, status=False, role="user", age=age, gender=gender)
        return True
        
    def valid_pass(self, Pass: str, token: str) -> str:
        if not valid_jwt(token=token).validation()["is_valid"]:
            return "none_pass"

        user_id = self.jwt.get_jwt(key="user_id", token=token)
        user = self.app.select(user_id)

        if not user:
            return "none_pass"

        password_db = user["password"]

        if self.hash.check_pw(data=Pass, new_data=password_db):
            return "true_pass"

        return "false_pass"

    
    def update_pass(self, token: str, current_password: str, new_pass: str) -> bool:
        auth = valid_jwt(token=token).validation()

        if not auth["is_valid"]:
            return False

        user_id = self.jwt.get_jwt(key="user_id", token=token)

        if user_id is None:
            return False

        user = self.app.select(user_id=user_id)

        if not user:
            return False

        password_hash = user["password"]

        if not self.hash.check_pw(
            data=current_password,
            new_data=password_hash
        ):
            return False

        if self.hash.check_pw(
            data=new_pass,
            new_data=password_hash
        ):
            return False

        self.app.update(
            user_id=user_id,
            password=self.hash.encoder_bcr(new_pass)
        )

        return True
    
    def valid_code(self, email: str, code: str) -> dict:
        from sqlalchemy import text
        from connect.manager_database import main_database
        from datetime import datetime, timedelta

        app = main_database()

       

        user = self.app.select_by_email(email=email)

       

        if not user:
            

            return {
                "status": False,
                "expired": False,
                "id": None
            }

        user_id = user["user_id"]
        code_input = str(code).strip()

        

        with app.connect() as session:
            result = session.execute(
                text("""
                    SELECT number, created_at
                    FROM validation
                    WHERE user_id = :user_id
                    AND CAST(number AS TEXT) = :code
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {
                    "user_id": user_id,
                    "code": code_input
                }
            )

            row = result.fetchone()

           

            if not row:
                

                return {
                    "status": False,
                    "expired": False,
                    "id": user_id
                }

            data = row._mapping
            created_at = data["created_at"]

           

            expired = datetime.now() > created_at + timedelta(minutes=10)

            

            if expired:
               

                session.execute(
                    text("DELETE FROM validation WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                session.commit()


                return {
                    "status": False,
                    "expired": True,
                    "id": user_id
                }

           

            session.execute(
                text("DELETE FROM validation WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            session.commit()

        

        return {
            "status": True,
            "expired": False,
            "id": user_id
        }
                
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
            
        
        
        
                
    def update_AuthPass(self, Pass:str, id:int) -> None:
        
        
        self.app.update(user_id=id, password=hash3().encoder_bcr(Pass))
        
        
    
    def update_name(self, new_name:str, token:str) -> dict:
          id = self.jwt.get_jwt(key="user_id", token=token)
          user = self.app.select(id)
          
          if user:
              if user["name"] == new_name:
                  return {"status": "equal"}
              
                  
              self.app.update(user_id=id, name=new_name)
              return {"status":True}
          
          return {"status":False}

    def update_username(self, new_username: str, token: str) -> dict:
          user_id = self.jwt.get_jwt(key="user_id", token=token)
          user = self.app.select(user_id)

          if not user:
              return {"status": False}

          if user["username"] == new_username:
              return {"status": "equal"}

          if self.app.select_by_username(new_username):
              return {"status": "exists"}

          self.app.update(user_id=user_id, username=new_username)
          return {"status": True, "username": new_username}

    def update_profile_image(self, profile_image: str | None, token: str) -> dict:
          user_id = self.jwt.get_jwt(key="user_id", token=token)
          user = self.app.select(user_id)

          if not user:
              return {"status": False}

          if profile_image and len(profile_image) > 1_500_000:
              return {"status": False, "message": "Imagem muito grande."}

          self.app.update(
              user_id=user_id,
              profile_image=profile_image,
              update_profile_image=True
          )

          return {"status": True, "profile_image": profile_image}
      
    def update_pass_by_user_id(self, user_id: int, new_pass: str) -> bool | str:
        user = self.app.select(user_id)

        if not user:
            return False

        if self.hash.check_pw(data=new_pass, new_data=user["password"]):
            return "equal"

        self.app.update(
            user_id=user_id,
            password=self.hash.encoder_bcr(new_pass)
        )

        return True
      
    def me(self, token: str) -> dict:
        auth = valid_jwt(token=token).validation()

        if not auth["is_valid"]:
            return {"status": False}

        user_id = self.jwt.get_jwt(key="user_id", token=token)

        if user_id is None:
            return {"status": False}

        user = self.app.select(user_id=user_id)

        if not user:
            return {"status": False}

        return {
            "status": True,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "username": user["username"],
                "profile_image": user["profile_image"],
                "email": user["email"],
                "age": user["age"],
                "gender": user["gender"],
                "role": user["role"],
            }
        }
    def check_delete_user(self, token: str, password: str) -> dict:
        auth = valid_jwt(token=token).validation()

        if not auth["is_valid"]:
            return {
                "status": False,
                "message": "Token inválido."
            }

        user_id = self.jwt.get_jwt(
            key="user_id",
            token=token
        )

        if user_id is None:
            return {
                "status": False,
                "message": "Usuário inválido."
            }

        user = self.app.select(user_id=user_id)

        if not user:
            return {
                "status": False,
                "message": "Usuário não encontrado."
            }

        password_hash = user["password"]

        if not self.hash.check_pw(password, password_hash):
            return {
                "status": False,
                "message": "Senha incorreta."
            }

        return {
            "status": True,
            "user_id": user_id
        }


    def delete_user_by_id(self, user_id: int) -> bool:
        return self.app.delete(user_id=user_id)
