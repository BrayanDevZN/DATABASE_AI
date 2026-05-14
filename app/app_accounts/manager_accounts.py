from app.app_accounts.repository import RepositoryAccount
from app.app_accounts.model import Model_user
from app.app_accounts.service import Service
from auth.manager_auth import Login, valid_jwt
from auth.auth_pass import Auth_Pass
from auth.auth_email import Auth_Create
from auth.hash import hash3
from app.app_accounts.repository import RepositoryAccount
from auth.jwt import JWT
from auth.dependences import Valid

class create_User:
    
    def env_code(self, data:dict) -> None:
        Data = Model_user(email=data["email"])
        
        code = Auth_Create(Data.email)
        code.execute()
        return Data.email
    
    def create(self, Data: dict) -> str | None:
        user = Model_user(
            email=Data["email"],
            name=Data["name"],
            password=Data["password"], 
            age=Data["age"],
            gender=Data["gender"]
        )

        valid_code = Service().valid_createAccount_code(
            email=user.email,
            code=Data["code"]
        )

        print(valid_code)  

        if valid_code["status"] and not valid_code["expired"]:
            Service().create_account(
                name=user.name,
                email=user.email,
                password=user.password,
                age=user.age,
                gender=user.gender
                
            )

            return Login(email=user.email, Pass=user.password).login()

        return None
    
    def valid_user(self, data:dict) -> bool:
        user = Model_user(name=data["email"]).email
        return {"exists":True} if RepositoryAccount().select_by_email(user) is not None else {"exists":False}
        
    
class User_Login:
    def login(self, data:dict) ->str:
            email = Model_user(email=data["email"]).email
            Pass = Model_user(password=data["password"]).password
            return Login(email=email, Pass=Pass).login()
        
    def Env_codePass(self, token:str) -> bool:
      
        new_token = valid_jwt(token).validation()
        if new_token["is_valid"]:
            id = JWT().get_jwt(key="user_id", token=token)
            email = JWT().get_jwt(key="email", token=token)
            env = Auth_Pass(id=id, email=email).execute()
            return True
        return False
    
    def updateAuth_Pass(self,data:dict) ->dict:
        code = data["code"]
        token = Model_user(token=data["token"]).token
        new_pass = Model_user(password=data["password"]).password
        
        new_token = valid_jwt(token).validation()
        valid_code = Service().valid_code(token=token, code=code)
        print(valid_code)
        if new_token["is_valid"] and (valid_code["status"] and not valid_code["expired"]):
            id = JWT().get_jwt(key="user_id", token=token)
            user = RepositoryAccount().select(id)
            password = user["password"]
            if hash3().check_pw(data=new_pass,  new_data=password):
                return {"status": "equal"}
            Service().update_AuthPass(token=token, Pass=new_pass)
            return {"status": True}
        return {"status": False}
    
    def check_pass(self, data: dict) -> dict:
        token = Model_user(token=data["token"]).token
        password = Model_user(password=data["password"]).password

        valid = Service().valid_pass(Pass=password, token=token)

        if valid != "true_pass":
            return {"status": False}

        user_id = JWT().get_jwt(key="user_id", token=token)

        change_token = JWT().token_password_change(user_id=user_id)

        return {
            "status": True,
            "change_token": change_token
        }

    def update_Pass(self, data: dict) -> dict:
        change_token = data["token"]
        new_password = Model_user(password=data["password"]).password

        payload = JWT().validate_password_change_token(change_token)

        if not payload["valid"]:
            return {"status": False}

        result = Service().update_pass_by_user_id(
            user_id=payload["user_id"],
            new_pass=new_password
        )

        return {"status": result}
    def update_name(self, data: dict) -> dict:
        token = Model_user(token=data["token"]).token
        new_name = Model_user(name=data["name"]).name

        valid_token = valid_jwt(token).validation()

        if not valid_token["is_valid"]:
            return {"status": False}

        result = Service().update_name(
            new_name=new_name,
            token=token
        )

        return result
    
    def valid_token(self, token:str) -> dict:
     
        valid_tk = valid_jwt(token=token["token"])
        return valid_tk.validation()
    
    

            
        
        


        
        
    
        
    
        
        