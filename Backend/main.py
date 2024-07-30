from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal, engine
from dto import UserRegistrationDTO, UserLoginDTO, UserResponseDTO, EventCreateDTO
from model import Base, User, Event
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime
from auth import get_password_hash, verify_password
import re

app = FastAPI()

# Create the tables provided in metadata
Base.metadata.create_all(bind = engine)

def validate_event_date(date_str: str) -> datetime:
    try:
        event_date = datetime.strptime(date_str, '%d-%m-%Y')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY.")
    
    if event_date < datetime.now():
        raise HTTPException(status_code=400, detail="The event date cannot be in the past.")
    
    return event_date.date().strftime('%d-%m-%Y')

def validate_event_time(time_str: str) -> datetime:
    try:
        event_time = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM.")
    
    return event_time.strftime('%H:%M')

# Fetch Database and Make a local session as long as we work on database
def get_db() :
    db = SessionLocal()

    try : 
        yield db
    finally : 
        db.close()

# Set up Database Dependency
db_dependency = Annotated[Session, Depends(get_db)]

#-#-#-#-#-# USER API #-#-#-#-#-#
# Create a Registration Function that posts to database
@app.post("/user/register", status_code=201)
def register_user(user_obj : UserRegistrationDTO, db : db_dependency):

    # Check if the email exists
    email_check = db.query(User).filter(User.email == user_obj.email).first()
    
    if email_check:
        raise HTTPException(status_code=400, detail= "User with same Email already exists")

    # Validate User Registration Entries
    if not user_obj.email :
        raise HTTPException(status_code=400, detail= "Email can not be empty")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",user_obj.email) : 
        raise HTTPException(status_code=400, detail= "Invalid Email Format")

    if not user_obj.phone :
        raise HTTPException(status_code=400, detail= "Please Enter Phone number")
    if len(user_obj.phone) < 10 :
        raise HTTPException(status_code=400, detail= "Invalid Phone number")

    if not user_obj.first_name.strip() :
        raise HTTPException(status_code=400, detail= "First Name is mandatory")
    
    # Validate the password
    if not user_obj.password or len(user_obj.password.strip()) == 0:
        raise HTTPException(status_code=400, detail = "Please Provide Password")
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@#$%^&+=]+$", user_obj.password):
        raise HTTPException(status_code=400, 
                            detail = "Weak Password detected. Use combination of Uppercase, lowercase and numbers")
    if len(user_obj.password) < 7 :
        raise HTTPException(status_code=400, detail = "Password should be atleast 7 characters")
    
    # Encrpt the password
    encrypted_pwd = get_password_hash(user_obj.password)

    # Define a user DTO object you want to pass
    user_obj = User(first_name = user_obj.first_name.strip(), 
                    last_name = user_obj.last_name, 
                    email = user_obj.email,
                    password = encrypted_pwd,
                    phone = user_obj.phone)
    
    db.add(user_obj)
    db.commit()
    return {"status_code" : 201 , "message" : "User Successfully Registered"}

@app.post("/user/login", status_code=200)
def login_user(user_login_obj : UserLoginDTO, db : db_dependency) :
    db_user = db.query(User).filter(User.email == user_login_obj.email).first()
    if not db_user : 
        raise HTTPException(status_code=401, detail = "Unregistered Email")
    if not verify_password(user_login_obj.password, db_user.password) :
        raise HTTPException(status_code=401, detail = "Invalid Credentials")
    user_passon_dto = UserResponseDTO(email=db_user.email,
                                      user_id = db_user.user_id,
                                      name = db_user.first_name + " " + db_user.last_name,
                                      phone = db_user.phone,
                                      privilege= db_user.privilege)
    return {"status_code" : 200, "message" : "Successfully Logged in..!", "body" : user_passon_dto}

#-#-#-#-#-# EVENT API #-#-#-#-#-#
# Create Event Function 
@app.post("/create-event", status_code=201)
def create_event(create_event_obj : EventCreateDTO, db : db_dependency):

    event_date = validate_event_date(create_event_obj.date_of_event)
    event_time = validate_event_time(create_event_obj.time_of_event)
    
    db_user = db.query(User).filter(create_event_obj.organizer_id == User.user_id).first()
    if not db_user : 
        raise HTTPException(status_code=404, detail="User with organiser_id not found")
    if len(create_event_obj.event_title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Title is mandatory")
    if len(create_event_obj.event_description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Description is mandatory")
    if len(create_event_obj.time_of_event.strip()) == 0:
        raise HTTPException(status_code=400, detail="Time is mandatory")
    if (len(create_event_obj.location.strip()) == 0) :
        raise HTTPException(status_code=400, detail="Location can not be empty")
    
    
    if db_user.privilege == "USER" :
        event_create_dto = Event(event_title = create_event_obj.event_title,
                             event_description = create_event_obj.event_description,
                             time_of_event = event_time,
                             date_of_event = event_date,
                             organizer_id = create_event_obj.organizer_id,
                             location = create_event_obj.location,
                             capacity = create_event_obj.capacity,
                             request_timestamp = datetime.now()
                             )
    else :
        event_create_dto = Event(event_title = create_event_obj.event_title,
                             event_description = create_event_obj.event_description,
                             time_of_event = event_time,
                             date_of_event = event_date,
                             organizer_id = create_event_obj.organizer_id,
                             location = create_event_obj.location,
                             capacity = create_event_obj.capacity,
                             request_timestamp = datetime.now(),
                             approved_timestamp = datetime.now(),
                             status = 'approved'
                             )
    db.add(event_create_dto)
    db.commit()
    return {"status_code" : 201, "message" : "Event successfully created"}

# Get All Events Function
@app.get("/all-events")
def get_all_events(db : db_dependency) :
    result = db.query(Event).all()
    return{"status_code" : 200, "body" : result}

@app.get("/pending-events")
def get_all_events(db : db_dependency) :
    result = db.query(Event).filter(Event.status == "pending").all()
    return{"status_code" : 200, "body" : result}

@app.get("/approved-events")
def get_all_events(db : db_dependency) :
    result = db.query(Event).filter(Event.status == "approved").all()
    return{"status_code" : 200, "body" : result}

@app.delete("/delete-event/{event_id}")
def delete_event(event_id : int, db:db_dependency):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="No Event with id found")
    db.delete(result)
    db.commit()
    return { "status_code" : 200, "message" : "Event deleted Successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)