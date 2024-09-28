from pydantic import BaseModel
from typing import Optional


# DTO for User Registration
class UserRegistrationDTO(BaseModel):
    first_name: str = None
    last_name: Optional[str] = None
    email: str = None
    password: str = None
    phone: str = None


# DTO for User Login
class UserLoginDTO(BaseModel):
    email: str = None
    password: str = None


# DTO for User Response
class UserResponseDTO(BaseModel):
    email: str
    user_id: int
    name: str
    phone: str
    log_id: int
    privilege: str


# DTO for Event Creation
class EventCreateDTO(BaseModel):
    event_title: str
    event_description: str
    time_of_event: str
    date_of_event: str
    organizer_id: int
    location: str
    capacity: int


# DTO for Event Updating
class EventUpdateDTO(BaseModel):
    event_title: str
    event_description: str
    time_of_event: str
    date_of_event: str
    organizer_id: int
    location: str
    capacity: int


# DTO for Event Registration
class RegisterForEvent(BaseModel):
    user_id: int
    attendee_name: str
    email: str
    phone: str = None
    event_id: int


# DTO for Getting Registered User
class GetRegisteredUserDTO(BaseModel):
    attendee_name: str
    email: str
    phone: str | None
    event_description: str
    time_of_event: str
    date_of_event: str
    location: str
    event_name: str
    registration_date: str


# DTO for Getting Events based on User
class GetUsersForEventDTO(BaseModel):
    attendee_name: str
    email: str
    phone: str | None
    registration_date: str


# DTO for Getting All Registrations of Events
class GetAllRegistrationsDTO(BaseModel):
    attendee_name: str
    email: str
    phone: str | None
    registered_by: str
    registration_date: str
    event_name: str
