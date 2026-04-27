
from sqlalchemy import create_engine
from dotenv import load_dotenv

class SupabaseConnect:
    def __init__(self, name:str, host:str, port:int, user:str, Pass:str) ->None:
        load_dotenv()
        self.__host = host
        self.__name = name
        self.__user = user
        self.__pass = Pass
        self.__port = port
        
    def base_url(self):
        return f"postgresql+psycopg://{self.__user}:{self.__pass}@{self.__host}:{self.__port}/{self.__name}"#CONNECTA COM O BANCO
    
    def connect(self):
        engine = create_engine(self.base_url())#RETORNA A CONEXÃO
        
   