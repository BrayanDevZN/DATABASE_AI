from pydantic import BaseModel,  Field, field_validator

class Model_user(BaseModel):
    
    name:str | None = None
    email:str | None = None
    token:str | None = None
    gender:str | None = None
    age:int | None = None
    password:str | None = Field(default=None ,min_length=8)
    role:str | None = Field(default="user")
    status:bool | None = Field(default=True)
    @field_validator("email")
    def valid_email(cls, v):
        if not "@gmail.com" in v:
            raise ValueError(f"not '@gmail.com' in {v}")
        
        if len(v.replace("@gmail.com", "")) <8:
            raise ValueError(f"{v.replace("@gmail.com", "")}: min len 8")
        
        return v
        
    @field_validator("password")
    def valid_pass(cls, v):
        if not any(c.isdigit()  for c in v):
            raise ValueError(f"not digit in {v}")
        if not any(c.islower()  for c in v):
            raise ValueError(f"not lower in {v}")
        if not any(c.isupper()  for c in v):
            raise ValueError(f"not upper in {v}")
        if not any(c.isalpha()  for c in v):
            raise ValueError(f"not letter in {v}")
        
        return v
