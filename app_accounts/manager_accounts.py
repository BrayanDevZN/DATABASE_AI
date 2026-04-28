from app_accounts.repository import RepositoryAccount
from app_accounts.model import Model_user
from app_accounts.service import Service
from auth.manager_auth import Login, valid_jwt
from auth.auth_pass import Auth_Pass
from auth.auth_email import CreateAccountCode
from auth.hash import hash3
from app_accounts.repository import RepositoryAccount

class create_User:
    
    def env_code(self, email:str) -> None:
        data = Model_user(email=email)
        
        code = CreateAccountCode(data.email)
        code.execute()
        return email
    
    def create(self, Data: dict) -> str | None:
        user = Model_user(
            email=Data["email"],
            name=Data["name"],
            password=Data["password"]
        )

        valid_code = Service().valid_createAccount_code(
            email=user.email,
            code=Data["code"]
        )

        print(valid_code)  # teste pra ver o que está vindo

        if valid_code["status"] and not valid_code["expired"]:
            Service().create_account(
                name=user.name,
                email=user.email,
                password=user.password
            )

            return Login(email=user.email, Pass=user.password).login()

        return None
    
    
aaa = create_User()
#aaa.env_code("flowr3898@gmail.com")
print(aaa.create({"email": "flowr3898@gmail.com", "password":"13Marco1978", "name":"brayan", "code":"216571"}))
    
        
        
        
        
        
        
        
    
        
        
    
        
        
    

    

        
        
    
        
    
        
        