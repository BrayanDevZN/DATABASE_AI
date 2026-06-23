
from sqlalchemy import URL, create_engine
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
        return URL.create(
            "postgresql+psycopg",
            username=self.__user,
            password=self.__pass,
            host=self.__host,
            port=self.__port,
            database=self.__name,
        )#CONNECTA COM O BANCO
    
    def connect(self):
        engine = create_engine(self.base_url())#RETORNA A CONEXÃO
        return engine
