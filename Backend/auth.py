from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(pwd) : 
    return password_context.hash(pwd)

def verify_password(plain_password, secured_password) :
    return password_context.verify(plain_password, secured_password)

