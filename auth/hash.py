
import bcrypt
class hash3:
    
    
    def encoder_bcr(self, data: str) -> str:
        return bcrypt.hashpw(
            data.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_pw(self, data: str, new_data: str) -> bool:
        

        return bcrypt.checkpw(
            data.encode("utf-8"),
            new_data.encode("utf-8")
        )
