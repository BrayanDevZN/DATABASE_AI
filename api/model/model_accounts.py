from pydantic import BaseModel, Field, field_validator


class ValidEmail(BaseModel): #valid_user e env_code
    data:dict
    @field_validator("data")
    def valid(cls, v):
        if len(v.keys()) > 1:
            raise ValueError("len > 1")
        if not "email" in v.keys():
            raise KeyError("not key 'email'")
        if type(v["email"]) !=str:
            raise ValueError("expeted str")
        
class CreateUser(BaseModel):
        data:dict
        @field_validator("data")
        def valid(cls, v):
            keys = ["email", "password", "name", "age", "gender", "code"]
            
            for c in v.items():
                    if type(c) !=str:
                        raise ValueError(f"{c} expeted str")
                        
                    if not c in keys:
                        raise KeyError(f"not {c}")
class Login(BaseModel):
        data:dict
        @field_validator("data")
        def valid(cls, v):
            keys = ["email", "password"]
            for c in keys:
                if type(c) !=str:
                        raise ValueError(f"{c} expeted str")
                        
                if not c in keys:
                        raise KeyError(f"not {c}")
    
class Env_CodePass(BaseModel):
        token:str
        
class UpdateAuthPass(BaseModel):
        data:dict
        @field_validator("data")
        def valid(cls, v):
            keys = ["code", "token", "password"]
            for c in keys:
                if c == "code" and type(c) != int:
                    raise ValueError(f"{c} expeted int")
                    
                if type(c) !=str:
                        raise ValueError(f"{c} expeted str")
                
                        
                if not c in keys:
                        raise KeyError(f"not {c}")
                    
class Pass(BaseModel): #check_pass e update_pass
        data:dict
        @field_validator("data")
        def valid(cls, v):
            keys = ["token", "password"]
            for c in keys:
                
                    
                if type(c) !=str:
                        raise ValueError(f"{c} expeted str")
                
                        
                if not c in keys:
                        raise KeyError(f"not {c}")
                    
class UpName(BaseModel): 
        data:dict
        @field_validator("data")
        def valid(cls, v):
            keys = ["token", "name"]
            for c in keys:
                
                    
                if type(c) !=str:
                        raise ValueError(f"{c} expeted str")
                
                        
                if not c in keys:
                        raise KeyError(f"not {c}")
            
                
                
                    
    
        
    
