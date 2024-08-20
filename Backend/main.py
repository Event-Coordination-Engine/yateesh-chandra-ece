from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal, engine
from dto import UserRegistrationDTO, UserLoginDTO, UserResponseDTO, EventCreateDTO, EventUpdateDTO, RegisterForEvent
from model import Base, User, Event, Attendee
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
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
    if db_user.last_name is None:
        db_user.last_name = ""
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
        raise HTTPException(status_code=404, detail="User has no previlege to organize event")
    if len(create_event_obj.event_title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Title is mandatory")
    if len(create_event_obj.event_description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Description is mandatory")
    if len(create_event_obj.time_of_event.strip()) == 0:
        raise HTTPException(status_code=400, detail="Time is mandatory")
    if (len(create_event_obj.location.strip()) == 0) :
        raise HTTPException(status_code=400, detail="Location can not be empty")
    
    e_title = db.query(Event).filter(Event.event_title == create_event_obj.event_title).first()
    if e_title is not None :
        raise HTTPException(status_code=409, detail = "Event Name already Exists..!")

    if create_event_obj.location != "online":

        event_datetime = datetime.strptime(f"{create_event_obj.date_of_event} {create_event_obj.time_of_event}", '%d-%m-%Y %H:%M')
        
        start_time_window = event_datetime - timedelta(hours=3)
        end_time_window = event_datetime + timedelta(hours=3)

        conflicting_event = db.query(Event).filter(
            Event.date_of_event == event_date,
            Event.location == create_event_obj.location.lower(),
            Event.time_of_event.between(start_time_window.time().strftime('%H:%M'), end_time_window.time().strftime('%H:%M'))
        ).first()

        if conflicting_event is not None:
            raise HTTPException(status_code=409, detail="Unable to register since there is a conflicting event.")

    if db_user.privilege == "USER" :
        event_create_dto = Event(event_title = create_event_obj.event_title,
                             event_description = create_event_obj.event_description,
                             time_of_event = event_time,
                             date_of_event = event_date,
                             organizer_id = create_event_obj.organizer_id,
                             location = create_event_obj.location.lower(),
                             capacity = create_event_obj.capacity,
                             request_timestamp = datetime.now()
                             )
    else :
        event_create_dto = Event(event_title = create_event_obj.event_title,
                             event_description = create_event_obj.event_description,
                             time_of_event = event_time,
                             date_of_event = event_date,
                             organizer_id = create_event_obj.organizer_id,
                             location = create_event_obj.location.lower(),
                             capacity = create_event_obj.capacity,
                             request_timestamp = datetime.now(),
                             approved_timestamp = datetime.now(),
                             status = 'approved'
                             )
    db.add(event_create_dto)
    db.commit()
    return {"status_code" : 201, "message" : "Event successfully created"}

@app.put("/event/{event_id}")
def update_event(update_event_obj: EventUpdateDTO, event_id: int, db: db_dependency):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="No Event found with Id")

    event_date = validate_event_date(update_event_obj.date_of_event)
    event_time = validate_event_time(update_event_obj.time_of_event)

    db_user = db.query(User).filter(update_event_obj.organizer_id == User.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User has no privilege to organize event")
    if len(update_event_obj.event_title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Title is mandatory")
    if len(update_event_obj.event_description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event Description is mandatory")
    if len(update_event_obj.time_of_event.strip()) == 0:
        raise HTTPException(status_code=400, detail="Time is mandatory")
    if len(update_event_obj.location.strip()) == 0:
        raise HTTPException(status_code=400, detail="Location cannot be empty")

    e_title = db.query(Event).filter(
        Event.event_title == update_event_obj.event_title,
        Event.event_id != event_id  # Exclude current event
    ).first()
    if e_title is not None:
        raise HTTPException(status_code=409, detail="Event Name already Exists..!")

    if update_event_obj.location != "online":
        event_datetime = datetime.strptime(f"{update_event_obj.date_of_event} {update_event_obj.time_of_event}", '%d-%m-%Y %H:%M')

        start_time_window = event_datetime - timedelta(hours=3)
        end_time_window = event_datetime + timedelta(hours=3)

        conflicting_event = db.query(Event).filter(
            Event.date_of_event == event_date,
            Event.location == update_event_obj.location.lower(),
            Event.event_id != event_id,  # Exclude current event
            Event.time_of_event.between(start_time_window.time().strftime('%H:%M'), end_time_window.time().strftime('%H:%M'))
        ).first()

        if conflicting_event is not None:
            raise HTTPException(status_code=409, detail="Unable to update since there is a conflicting event.")

    # Update the existing event with the new data
    result.event_title = update_event_obj.event_title
    result.event_description = update_event_obj.event_description
    result.time_of_event = event_time
    result.date_of_event = event_date
    result.organizer_id = update_event_obj.organizer_id
    result.location = update_event_obj.location.lower()
    result.capacity = update_event_obj.capacity
    result.request_timestamp = datetime.now()

    if db_user.privilege != "USER":
        result.approved_timestamp = datetime.now()
        result.status = 'approved'

    db.commit()
    return {"status_code": 200, "message": "Event successfully updated"}

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

@app.get("/event/{event_id}")
def get_event_by_id(event_id : int, db: db_dependency):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None :
        raise HTTPException(status_code=404, detail="No event found with Id")
    return {"status_code" : 200, "body" : result}

@app.get("/event_by_user/{user_id}")
def get_event_by_user_id(user_id : int, db : db_dependency):
    result = db.query(Event).filter(Event.organizer_id == user_id).all()
    if result is None:
        raise HTTPException(status_code=404, detail = "No event organised by this user")
    return {"status_code" : 200, "body" : result}

@app.get("/event_by_user/pending/{user_id}")
def get_event_by_user_id(user_id : int, db : db_dependency):
    result = db.query(Event).filter(Event.organizer_id == user_id).filter(Event.status == "pending").all()
    if result is None:
        raise HTTPException(status_code=404, detail = "No event organised by this user")
    return {"status_code" : 200, "body" : result}

@app.put("/approve-event/{event_id}")
def approve_event(event_id : int, db : db_dependency):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None :
        raise HTTPException(status_code=404, detail="No event with Id")
    if result.status == "approved":
        raise HTTPException(status_code=409, detail="This event is already approved")
    result.approved_timestamp = datetime.now()
    result.status = "approved"
    db.commit()
    return {"status_code" : 200, "message" : "event approved"}

@app.post("/register_event", status_code=201)
def register_for_event(reg_dto : RegisterForEvent , db : db_dependency):
    user_check = db.query(User).filter(User.user_id == reg_dto.user_id).first()
    if user_check is None :
        raise HTTPException(status_code=404, detail=f"User with User ID : {reg_dto.user_id} does not exist")
    elif user_check.privilege == "ADMIN":
        raise HTTPException(status_code=409, detail="Admins cannot register for an event")
    
    event_check = db.query(Event).filter(Event.event_id == reg_dto.event_id).first()
    if event_check is None :
        raise HTTPException(status_code=404, detail=f"Event with Event ID : {reg_dto.event_id} does not exist")
    elif event_check.status != 'approved':
        raise HTTPException(status_code=409, detail="Unable to register since Event is not yet approved")
    elif event_check.organizer_id == reg_dto.user_id:
        raise HTTPException(status_code=409, detail="Cannot register since user is organiser")
    
    email_check = db.query(Attendee).filter(Attendee.email == reg_dto.email).first()
    event_count = db.query(Attendee).filter(Attendee.event_id == reg_dto.event_id).count()
    if event_count >= event_check.capacity:
        raise HTTPException(status_code=409, detail="Cannot Register since max Capacity reached")
    if email_check :
        raise HTTPException(status_code=409, detail="Email Already registered")
    if not reg_dto.email.strip() :
        raise HTTPException(status_code=400, detail= "Email can not be empty")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",reg_dto.email) : 
        raise HTTPException(status_code=400, detail= "Invalid Email Format")
    

    registration_obj = Attendee(user_id = reg_dto.user_id,
                                attendee_name = reg_dto.attendee_name,
                                email = reg_dto.email,
                                phone = reg_dto.phone,
                                event_id = reg_dto.event_id)
    db.add(registration_obj)
    db.commit()
    return {"status_code" : 201, "message" : "Registered for the event successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000", "http://localhost:5000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)