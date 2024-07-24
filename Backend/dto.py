from model import User
from pydantic import BaseModel

# Create a DTO for User Registration
class UserRegistrationDTO(BaseModel) : 
    first_name : str = None
    last_name : str = None
    email : str = None
    password : str = None
    phone : str = None