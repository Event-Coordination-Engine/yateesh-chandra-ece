from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# DTO for User Registration
class UserRegistrationDTO(BaseModel) : 
    first_name : str = None
    last_name : Optional[str] = None
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

# DTO for Event
class EventCreateDTO(BaseModel):
    event_title : str
    event_description :str
    time_of_event : str
    date_of_event : str
    organizer_id : int
    location : str
    capacity : int

class EventUpdateDTO(BaseModel):
    event_title : str
    event_description :str
    time_of_event : str
    date_of_event : str
    organizer_id : int
    location : str
    capacity : int

class RegisterForEvent(BaseModel):
    user_id : int
    attendee_name : str
    email : str
    phone : str = None
    event_id : int