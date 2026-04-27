import hashlib
import bcrypt
class hash3:
    def encoder_hash(self, data:str) -> str: #converte em hash sha3_256(não recomendado pra senha)
        hash_data = hashlib.sha3_256(data.encode()).hexdigest()
        return hash_data
    
    def encoder_bcr(self, data:str) -> str: 
        return bcrypt.hashpw(data.encode(), bcrypt.gensalt())
    
    def check_pw(self, data:str, new_data:bytes) ->bool:
        return bcrypt.checkpw(
            data.encode("utf_8"), 
            new_data
        )
        
