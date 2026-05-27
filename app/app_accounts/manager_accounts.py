from app.app_accounts.repository import RepositoryAccount
from app.app_accounts.model import Model_user
from app.app_accounts.service import Service
from auth.manager_auth import Login, valid_jwt
from auth.auth_sender import Sender_Auth
from auth.hash import hash3
from app.app_accounts.repository import RepositoryAccount
from auth.jwt import JWT
from auth.dependences import Valid
from app.app_conversations.manager_conversation import ManagerConversation



def delete_user(self, data: dict) -> dict:
    token = data["token"]
    password = data["password"]

    check = Service().check_delete_user(
        token=token,
        password=password
    )

    if not check["status"]:
        return check

    ManagerConversation().delete_all_by_user(
        user_id=check["user_id"]
    )

    deleted = Service().delete_user_by_id(
        user_id=check["user_id"]
    )

    return {
        "status": deleted
    }

class create_User:
    
    def env_code(self, data:dict) -> None:
        Data = Model_user(email=data["email"])
        
        code = Sender_Auth(content=Data.email, type="Create")()
        
        return "Ok"
    
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
        user = Model_user(email=data["email"]).email
        return {"exists": RepositoryAccount().select_by_email(user) is not None} 
        
    
class User_Login:
    def login(self, data:dict) ->str:
            email = Model_user(email=data["email"]).email
            Pass = Model_user(password=data["password"]).password
            return Login(email=email, Pass=Pass).login()
        
    def Env_codePass(self, data: dict) -> dict:
        token = data.get("token")
        email = data.get("email")

        user_id = None

        if token:
            new_token = valid_jwt(token=token).validation()

            if not new_token["is_valid"]:
                return {"status": False}

            user_id = JWT().get_jwt(key="user_id", token=token)
            email = JWT().get_jwt(key="email", token=token)

        elif email:
            user = RepositoryAccount().select_by_email(email=email)

            if not user:
                return {"status": False}

            user_id = user["user_id"]
            email = user["email"]

        else:
            return {"status": False}

        if not user_id or not email:
            return {"status": False}

        Sender_Auth(
            type="Update",
            content={
                "id": user_id,
                "email": email
            }
        )()

        return {
            "status": True,
            "email": email
        }
        
       
    
    def updateAuth_Pass(self, data: dict) -> dict:
        code = data["code"]

        email = data.get("email")
        token = data.get("token")

        if not email and token:
            email = JWT().get_jwt(
                key="email",
                token=token
            )

        if not email:
            return {"status": False}

        new_pass = Model_user(
            password=data["password"]
        ).password

        valid_code = Service().valid_code(
            email=email,
            code=code
        )

        if valid_code["status"] and not valid_code["expired"]:
            user = RepositoryAccount().select_by_email(
                email=email
            )

            password = user["password"]

            if hash3().check_pw(
                data=new_pass,
                new_data=password
            ):
                return {"status": "equal"}

            Service().update_AuthPass(
                id=valid_code["id"],
                Pass=new_pass
            )

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
        token = data["token"]
        current_password = data["current_password"]
        new_password = Model_user(password=data["password"]).password

        result = Service().update_pass(
            token=token,
            current_password=current_password,
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
    
    def me(self, data: dict) -> dict:
        token = data["token"]

        return Service().me(token=token)
    
    def delete_user(self, data: dict) -> dict:
        token = data["token"]
        password = data["password"]

        check = Service().check_delete_user(
            token=token,
            password=password
        )

        if not check["status"]:
            return check

        ManagerConversation().delete_all_by_user(
            user_id=check["user_id"]
        )

        deleted = Service().delete_user_by_id(
            user_id=check["user_id"]
        )

        return {
            "status": deleted
        }
        
    
    

            
        
        


        
        
    
        
    
        
        