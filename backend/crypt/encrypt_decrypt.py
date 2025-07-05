import bcrypt
import re
import random
import string

class EncryptionDec:

    def __init__(self):
        pass

    def hash_password(self,text:str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(text.encode('utf-8'),salt)
        return hashed.decode('utf-8')

    def check_passwords(self,plain_text:str,passwd:str) -> bool:
        return bcrypt.checkpw(plain_text.encode('utf-8'),passwd.encode('utf-8'))

    def is_valid_password(self,password:str) -> bool:
        if len(password) < 8: 
            return False
        
        has_lower = re.search(r"[a-z]",password)
        has_upper = re.search(r"[A-Z]",password)
        has_digit = re.search(r"\d",password)
        has_special = re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)

        return all([has_lower,has_upper,has_digit,has_special])

    def generate_verification_code(self,length=6):
        return ''.join(random.choices(string.digits,k=length))
    

