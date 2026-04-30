import os
from dotenv import load_dotenv
from pathlib import Path
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env", override=True)
class data:
    def __init__(self) -> None:   #ESSA CLASSE SERVE PRA PEGAR OS DADOS DO BANCO DE DADOS
        
        self.__dbname = os.getenv("DB_NAME")
        self.__dbUser = os.getenv("DB_USER")
        self.__dbport = int(os.getenv("DB_PORT"))
        self.__dbhost = os.getenv("DB_HOST")
        self.__dbpass = os.getenv("DB_PASSWORD")
        self.__secret = os.getenv("SECRET")
        self.__email_key = os.getenv("KEY_EMAIL")
        self.__email = os.getenv("EMAIL_USER")
        
    def db_name(self) -> str:
        return self.__dbname
    
    def db_user(self) -> str:
        return self.__dbUser
    
     
    def db_port(self) -> str:
        return self.__dbport
    
     
    def db_host(self) -> str:
        return self.__dbhost
    
     
    def db_pass(self) -> str:
        return self.__dbpass
    
    def secret(self) ->str:
        return self.__secret
    
    def key_email(self) -> str:
        return self.__email_key
    def email_user(self) -> str:
        return self.__email
    
        
    
