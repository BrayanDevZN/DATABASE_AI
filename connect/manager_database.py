from connect.database import SupabaseConnect
from core.config import data

def main_database():#CHAMA CONGIG E DATABASE E CONECTA TUDO
    dbdata = data()
    con = SupabaseConnect(name=dbdata.db_name(), host=dbdata.db_host(), user=dbdata.db_user(), port=dbdata.db_port(), Pass=dbdata.db_pass())
    return con.connect()