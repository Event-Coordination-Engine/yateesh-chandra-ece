from passlib.context import CryptContext

# Creating Context for BCrypt Algorithm
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Get the Encrypted Password
def get_password_hash(pwd):
    return password_context.hash(pwd)


# Verification of password for Secured and Plain ones
def verify_password(plain_password, secured_password):
    return password_context.verify(plain_password, secured_password)
