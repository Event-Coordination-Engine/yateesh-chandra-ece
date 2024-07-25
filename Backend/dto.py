from model import User
from pydantic import BaseModel

# Create a DTO for User Registration
class UserRegistrationDTO(BaseModel) : 
    first_name : str = None
    last_name : str = None
    email : str = None
    password : str = None
    phone : str = None

class UserLoginDTO(BaseModel) :
    email : str = None
    password : str = None

class UserResponseDTO(BaseModel) :
    email : str
    user_id : int
    name : str
    phone : str
    privilege : str