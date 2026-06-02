from auth.dependences import Valid
from auth.hash import hash3
from auth.jwt import JWT
from connect.manager_database import main_database
from sqlalchemy import  text

engine = main_database()
Valid_data = Valid()
data = JWT()

class Login:
    def __init__(self, email:str, Pass:str) -> None:
        self.email = email
        
        self.Pass = Pass
        self.hash = hash3()
        self.db = self.read()
        self.hashPass =  Pass
       
        
    def read(self) -> dict:
        
        with engine.connect() as session:
            data = session.execute(
            text("""
                SELECT user_id, name, username, age, gender, email, password, role, status, profile_image
                FROM users
                WHERE email = :email
            """),
            {"email": self.email}
        )

            user = data.fetchone()

            return {
                "user_id": user[0],
                "name": user[1],
                "username": user[2],
                "age": user[3],
                "gender": user[4],
                "email": user[5],
                "password": user[6],
                "role": user[7],
                "status": user[8],
                "profile_image": user[9]
            } if user is not None else None
            
    def valid_pass(self) -> bool:
        check = Valid_data.valid_pass(value=self.Pass, check_value=self.db["password"])
        return check
    
    
    def login(self) -> str | bool | dict:
        
        if self.db is None:
            return {"exists":False, "status": False, "token":None}
        
        if not self.valid_pass():
            return {"exists":True, "status": False, "token":None}
        token = data.token(email=self.db["email"], user_id=self.db["user_id"], role=self.db["role"], status=self.db["status"])
        return {"exists":True, "status": True, "token":token, "name": self.db["name"], "username": self.db["username"], "profile_image": self.db["profile_image"], "gender": self.db["gender"], "age":self.db["age"]}
 
    
class valid_jwt:
    def __init__(self, token:str):
        self.token = token
        
        
    def check_jwt(self) -> bool:
        return Valid_data.auth_jwt(self.token)
    
    def check_admin(self) -> bool:
        return Valid_data.auth_admin(self.token)
    
    def validation(self) ->dict:
        return {
            "admin": self.check_admin(), 
            "is_valid": self.check_jwt(),
            "token": self.token
        }
