import os
from dotenv import load_dotenv
class data:
    def __init__(self) -> None:   #ESSA CLASSE SERVE PRA PEGAR OS DADOS DO BANCO DE DADOS
        load_dotenv()
        self.__dbname = os.getenv("DB_NAME")
        self.__dbUser = os.getenv("DB_USER")
        self.__dbport = os.getenv("DB_PORT")
        self.__dbhost = os.getenv("DB_HOST")
        self.__dbpass = os.getenv("DB_PASSWORD")
        self.__secret = os.getenv("SECRET")
        
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
        
    
        
        
        
print(data().db_host())