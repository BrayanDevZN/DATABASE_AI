from dependences import Valid
from hash import hash3
from jwt import JWT
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
        self.hashPass =  self.hash.encoder_hash(self.Pass)
       
        
    def read(self) -> dict:
        
        email =  self.hash.encoder_hash(self.email)
        with engine.connect() as session:
                data = session.execute(text('SELECT * from Users where email= :email'), {"email": email})
                user = data.fetchone()
                
                return  {
                    "user_id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "password": user[3],
                    "role": user[4],
                    "status": user[5]
                } if user is not None else None
            
    def valid_pass(self) -> bool:
        check = Valid_data.valid_pass(value=self.Pass, check_value=self.db["password"])
        return check
    
    def login(self) -> str | bool | dict:
        if self.db is None:
            return {"status": False}
        
        if not self.valid_pass():
            return "invalid pass"
        token = data.token(email=self.db["email"], user_id=self.db["user_id"], role=self.db["role"], status=self.db["status"])
        return token
 
    
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
        
        
        
    
        
    
    
        
        
        
        
        
        
        
    
            

            
        
                
            
            
        
        
        
        
        
    
        
        