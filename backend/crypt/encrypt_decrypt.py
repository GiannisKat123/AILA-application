import bcrypt

class EncryptionDec:

    def __init__(self):
        pass

    def hash_password(self,text:str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(text.encode('utf-8'),salt)
        return hashed.decode('utf-8')

    def check_passwords(self,plain_text:str,passwd:str) -> bool:
        return bcrypt.checkpw(plain_text.encode('utf-8'),passwd.encode('utf-8'))