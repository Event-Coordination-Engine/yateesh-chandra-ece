from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal, engine
from dto import UserRegistrationDTO, UserLoginDTO, UserResponseDTO,\
    EventCreateDTO, EventUpdateDTO, RegisterForEvent, GetRegisteredUserDTO, GetUsersForEventDTO,\
    GetAllRegistrationsDTO
from model import Base, User, Event, Attendee, UserLog, EventBackUp, EventOpsLog, Attendee_Bkp
from typing import Annotated, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from auth import get_password_hash, verify_password
import re
from sqlalchemy import update, func
import utils
import json
from threading import Thread

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

def cleanUpOlderData():
    db: Session = next(get_db())
    curr_date = datetime.now().strftime("%d-%m-%Y")
    print(curr_date)
    inactive_events = db.query(Event).filter(func.to_date(Event.date_of_event, 'DD-MM-YYYY') < curr_date).all()
    if len(inactive_events) == 0 :
        print("No earlier events to be Cleaned")
    else :
        print(f"Cleaning up {len(inactive_events)} events : ")
        cnt = 1
        for event in inactive_events:
            print(f"{cnt}. {event.event_title} - {event.date_of_event}")
            
            # Updating the Status in Event Backup table to inactive and latest op to Delete
            db.query(EventBackUp).filter(EventBackUp.event_id == event.event_id).update(
                {EventBackUp.flag: "inactive",EventBackUp.latest_op: "DELETE", EventBackUp.op_tstmp:datetime.now()},
                synchronize_session=False
            )
            
            # Updating the reg_status in Attendees Backup Table to inactive for all the events who are cleaned up
            db.query(Attendee_Bkp).filter(Attendee_Bkp.event_id == event.event_id).update(
                {Attendee_Bkp.reg_status: "inactive"},
                synchronize_session=False
            )

            # Adding the Delete Log to the Event Operations
            log_obj = EventOpsLog(event_id = event.event_id
                                  , op_type = "DELETE"
                                  , op_desc = "This Event is expired and hence cleaned up" 
                                  , op_tstmp = datetime.now())
            db.add(log_obj)
            db.delete(event)
            db.commit()
            cnt += 1
        print(f"Clean-Up Completed")
    
def start_background_task():
    task_thread = Thread(target=cleanUpOlderData)
    # Allows thread to exit when the main program exits
    task_thread.daemon = True  
    task_thread.start()

@app.on_event("startup")
async def startup_event():
    start_background_task()

#-#-#-#-#-# USER API #-#-#-#-#-#
# Create a Registration Function that posts to database
@app.post("/user/register", status_code=201)
def register_user(user_obj : UserRegistrationDTO, db : db_dependency, background_tasks: BackgroundTasks):

    # Check if the email exists
    email_check = db.query(User).filter(func.lower(User.email) == user_obj.email.strip().lower()).first()
    
    if email_check : 
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
                    registered_date = datetime.now(),
                    phone = user_obj.phone)
    
    db.add(user_obj)
    user_name = user_obj.first_name + " " + user_obj.last_name if user_obj.last_name is not None else user_obj.first_name
    background_tasks.add_task(utils.registration_email, user_obj.email, user_name)
    db.commit()
    return {"status_code" : 201 , "message" : "User Successfully Registered"}

@app.post("/user/login", status_code=200)
def login_user(user_login_obj : UserLoginDTO, db : db_dependency):
    db_user = db.query(User).filter(User.email == user_login_obj.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Unregistered Email")
    if not verify_password(user_login_obj.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if db_user.last_name is None:
        db_user.last_name = ""

    db.query(UserLog).filter(UserLog.user_id == db_user.user_id, UserLog.logout_tstmp == None).update(
        {UserLog.logout_tstmp: datetime.now()},
        synchronize_session=False
    )
    db.commit()

    # Create a new login session
    login_obj = UserLog(user_id=db_user.user_id, login_tstmp=datetime.now())
    db.add(login_obj)
    db.commit()

    user_passon_dto = UserResponseDTO(
        email=db_user.email,
        user_id=db_user.user_id,
        name=db_user.first_name + " " + db_user.last_name,
        phone=db_user.phone,
        log_id=login_obj.log_id,
        privilege=db_user.privilege
    )

    return {"status_code": 200, "message": "Successfully Logged in..!", "body": user_passon_dto}

@app.put("/user/logout/{log_id}")
def logout_user(log_id : int, db:db_dependency):
    user_obj = db.query(UserLog).filter(UserLog.log_id == log_id).first()
    if user_obj is None : 
        raise HTTPException(status_code=401, detail="No Active Session found")
    user_obj.logout_tstmp = datetime.now()
    db.commit()
    return {"status_code" : 200, "message" : "Suceessfully Logged out"}

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
    
    if not create_event_obj.capacity :
        raise HTTPException(status_code=400, detail="Capacity can not be empty")
    elif create_event_obj.capacity <= 0 :
        raise HTTPException(status_code=400, detail="Capacity can not be zero or invalid")
    
    e_title = db.query(Event).filter(Event.event_title == create_event_obj.event_title).first()
    if e_title is not None :
        raise HTTPException(status_code=409, detail = "Event Name already Exists..!")

    if create_event_obj.location.lower() != "online":

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
    x = json.dumps(create_event_obj.dict())

    res = db.query(Event).filter(Event.event_title == event_create_dto.event_title).first()
    event_bkp_dto = EventBackUp(
                        event_id= res.event_id,
                        event_title = res.event_title,
                        event_description = res.event_description,
                        time_of_event = res.time_of_event,
                        date_of_event = res.date_of_event,
                        organizer_id = res.organizer_id,
                        location = res.location,
                        capacity = res.capacity,
                        request_timestamp = res.request_timestamp,
                        approved_timestamp = res.approved_timestamp,
                        status=res.status,
                        latest_op = 'POST',
                        op_tstmp = datetime.now()
                        )
    log_obj = EventOpsLog(event_id = res.event_id, op_type = "POST", op_desc = x + " is added", op_tstmp = datetime.now())
    db.add(event_bkp_dto)
    db.add(log_obj)
    db.commit()
    return {"status_code" : 201, "message" : "Event successfully created"}

@app.put("/event/{event_id}")
def update_event(update_event_obj: EventUpdateDTO, event_id: int, db: db_dependency):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    result_bkp = db.query(EventBackUp).filter(EventBackUp.event_id == event_id).first()
    print(update_event_obj.date_of_event)
    update_dict = update_event_obj.dict()

    # Convert result (Event model instance) to a dictionary
    result_dict = {key: value for key, value in result.__dict__.items() if not key.startswith('_')}

    changes = []
    for key, update_value in update_dict.items():
        result_value = result_dict.get(key)
        if update_value != result_value:
            changes.append(f"{key} changed from {result_value} to {update_value}")

    # Prepare the message
    if changes:
        message = ", ".join(changes)
    else:
        message = "No Changes Done"

    print(message)

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
    result_bkp.event_id = event_id
    result.event_title = result_bkp.event_title = update_event_obj.event_title
    result.event_description =  result_bkp.event_description = update_event_obj.event_description
    result.time_of_event = result_bkp.time_of_event = event_time
    result.date_of_event = result_bkp.date_of_event = event_date
    result.organizer_id = result_bkp.organizer_id = update_event_obj.organizer_id
    result.location = result_bkp.location = update_event_obj.location.lower()
    result.capacity = result_bkp.capacity = update_event_obj.capacity
    result.request_timestamp = result_bkp.request_timestamp = datetime.now()
    result.status = result_bkp.status = 'pending'
    result_bkp.latest_op = 'PUT'
    result_bkp.op_tstmp = datetime.now()

    if db_user.privilege != "USER":
        result.approved_timestamp = result_bkp.approved_timestamp = datetime.now()
        result.status = result_bkp.status = 'approved'

    log_obj = EventOpsLog(event_id = event_id, op_type = "PUT", op_desc = message , op_tstmp = datetime.now())
    db.add(log_obj)
    db.commit()
    return {"status_code": 200, "message": "Event successfully updated"}

# Get All Events Function
@app.get("/all-events")
def get_all_events(db : db_dependency) :
    result = db.query(Event).all()
    return{"status_code" : 200, "body" : result}

@app.get("/pending-events")
def get_pending_events(db : db_dependency) :
    result = db.query(Event).filter(Event.status == "pending").all()
    return{"status_code" : 200, "body" : result}

@app.get("/approved-events")
def get_approved_events(db : db_dependency) :
    date_to_show = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    result = db.query(Event).filter(Event.status == "approved",  
                                    func.to_date(Event.date_of_event, 'DD-MM-YYYY') >= date_to_show
                                    ).all()
    return{"status_code" : 200, "body" : result}

@app.get("/available-events/{user_id}")
def get_available_events(user_id : int, db : db_dependency) :
    date_to_show = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    result = db.query(Event).filter(Event.status == "approved", Event.organizer_id != user_id, func.to_date(Event.date_of_event, 'DD-MM-YYYY') >= date_to_show).all()
    return{"status_code" : 200, "body" : result}

@app.delete("/delete-event/{event_id}")
def delete_event(event_id : int, db:db_dependency):
    db.query(EventBackUp).filter(EventBackUp.event_id == event_id).update(
        {EventBackUp.flag: "inactive",EventBackUp.latest_op: "DELETE", EventBackUp.op_tstmp:datetime.now()},
        synchronize_session=False
    )
    db.query(Attendee_Bkp).filter(Attendee_Bkp.event_id == event_id).update(
        {Attendee_Bkp.reg_status: "inactive"},
        synchronize_session=False
    )
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="No Event with id found")
    db.delete(result)
    log_obj = EventOpsLog(event_id = event_id, op_type = "DELETE", op_desc = "This Event is Deleted" , op_tstmp = datetime.now())
    db.add(log_obj)
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
def get_pending_event_by_user_id(user_id : int, db : db_dependency):
    result = db.query(Event).filter(Event.organizer_id == user_id).filter(Event.status == "pending").all()
    if result is None:
        raise HTTPException(status_code=404, detail = "No event organised by this user")
    return {"status_code" : 200, "body" : result}

@app.put("/approve-event/{event_id}")
def approve_event(event_id : int, db : db_dependency, background_tasks : BackgroundTasks):
    result = db.query(Event).filter(Event.event_id == event_id).first()
    result_bkp = db.query(EventBackUp).filter(EventBackUp.event_id == event_id).first()
    if result is None :
        raise HTTPException(status_code=404, detail="No event with Id")
    if result.status == "approved":
        raise HTTPException(status_code=409, detail="This event is already approved")
    result.approved_timestamp = result_bkp.approved_timestamp = datetime.now()
    result.status = result_bkp.status = "approved"
    log_obj = EventOpsLog(event_id = event_id, op_type = "PUT", op_desc = "Your event got approved by admin" , op_tstmp = datetime.now())
    db.add(log_obj)
    user = db.query(User).filter(result.organizer_id == User.user_id).first()
    user_name = user.first_name + " " + user.last_name if user.last_name is not None else user.first_name
    background_tasks.add_task(utils.approval_email, user_name, result.event_title, result.date_of_event, result.time_of_event, result.location, result.event_description, user.email)
    db.commit()
    return {"status_code" : 200, "message" : "event approved"}

@app.put("/approve-all-events")
def approve_all_event(db : db_dependency, background_tasks : BackgroundTasks):
    result = db.query(Event).filter(Event.status == "pending").all()
    result_bkp = db.query(EventBackUp).filter(EventBackUp.status == "pending").all()
    for i in result :
        i.approved_timestamp = datetime.now()
        i.status = "approved"
        user = db.query(User).filter(i.organizer_id == User.user_id).first()
        user_name = user.first_name + " " + user.last_name if user.last_name is not None else user.first_name
        background_tasks.add_task(utils.approval_email, user_name, i.event_title, i.date_of_event, i.time_of_event, i.location, i.event_description, user.email)
        db.commit()
    for i in result_bkp :
        i.approved_timestamp = datetime.now()
        i.status = "approved"
        log_obj = EventOpsLog(event_id = i.event_id, op_type = "PUT", op_desc = "Your event got approved by admin" , op_tstmp = datetime.now())
        db.add(log_obj)
        db.commit()
    return {"status_code" : 200, "message" : "events approved"}

@app.post("/register_event", status_code=201)
def register_for_event(reg_dto: RegisterForEvent, db: db_dependency):
    user_check = db.query(User).filter(User.user_id == reg_dto.user_id).first()
    if user_check is None:
        raise HTTPException(status_code=404, detail=f"User with User ID: {reg_dto.user_id} does not exist")
    
    event_check = db.query(Event).filter(Event.event_id == reg_dto.event_id).first()
    if event_check is None:
        raise HTTPException(status_code=404, detail=f"Event with Event ID: {reg_dto.event_id} does not exist")
    elif event_check.status != 'approved':
        raise HTTPException(status_code=409, detail="Unable to register since Event is not yet approved")
    elif event_check.organizer_id == reg_dto.user_id:
        raise HTTPException(status_code=409, detail="Cannot register since user is organizer")
    
    # Check if the email is already registered for the same event
    email_check = db.query(Attendee).filter(Attendee.email == reg_dto.email, Attendee.event_id == reg_dto.event_id).first()
    if email_check is not None:
        if email_check.users.privilege == "ADMIN":
            raise HTTPException(status_code=409, detail="Oops. Admin is blocked from Registration.!")
        raise HTTPException(status_code=409, detail="Email already registered for this event")

    event_count = db.query(Attendee).filter(Attendee.event_id == reg_dto.event_id).count()
    if event_count >= event_check.capacity:
        raise HTTPException(status_code=409, detail="Cannot register since max Capacity reached")

    if not reg_dto.email.strip():
        raise HTTPException(status_code=400, detail="Email cannot be empty")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", reg_dto.email):
        raise HTTPException(status_code=400, detail="Invalid Email Format")
    if reg_dto.phone:
        if len(reg_dto.phone) < 10:
            raise HTTPException(status_code=400, detail="Phone Number should not be less than 10 digits")

    registration_obj = Attendee(
        user_id=reg_dto.user_id,
        attendee_name=reg_dto.attendee_name,
        email=reg_dto.email,
        phone=reg_dto.phone,
        event_id=reg_dto.event_id
    )
    reg_obj = Attendee_Bkp(
        user_id=reg_dto.user_id,
        attendee_name=reg_dto.attendee_name,
        email=reg_dto.email,
        phone=reg_dto.phone,
        event_id=reg_dto.event_id,
        reg_status='active'
    )
    db.add(reg_obj)
    db.add(registration_obj)
    db.commit()
    return {"status_code": 201, "message": "Registered for the event successfully"}


@app.get("/registered_event/users/{user_id}")
def get_registered_events_by_event_id(user_id: int, db: db_dependency):

    result = db.query(Attendee).filter(Attendee.user_id == user_id).all()

    return_dto: List[GetRegisteredUserDTO] = []

    for attendee in result:

        event = db.query(Event).filter(Event.event_id == attendee.event_id).first()

        dto = GetRegisteredUserDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            event_name=event.event_title if event else None, 
            event_description=event.event_description,
            time_of_event=event.time_of_event,
            date_of_event=event.date_of_event,
            location=event.location,
            registration_date=datetime.strftime(attendee.registration_timestamp.date(), '%d-%m-%Y')
        )
        return_dto.append(dto)

    return {"status": 200, "message": "Events fetched successfully", "body": return_dto}

@app.get("/registered_event/events/{event_id}")
def get_registered_events_by_event_id(event_id: int, db: db_dependency):

    result = db.query(Attendee).filter(Attendee.event_id == event_id).all()
    return_dto: List[GetUsersForEventDTO] = [
        GetUsersForEventDTO(attendee_name=attendee.attendee_name,
                            email=attendee.email,
                            phone=attendee.phone,
                            registration_date=datetime.strftime(attendee.registration_timestamp.date(), '%d-%m-%Y')) for attendee in result
    ]
    return {"status": 200, "message": "Registrations fetched successfully", "body": return_dto}

@app.get("/all_registered_events")
def get_all_registered_events(db: db_dependency):

    result = db.query(Attendee).all()

    return_dto: List[GetAllRegistrationsDTO] = []

    for attendee in result:

        event = db.query(Event).filter(Event.event_id == attendee.event_id).first()
        user = db.query(User).filter(User.user_id == attendee.user_id).first()

        user_name = user.first_name
        if user.last_name:
            user_name = user_name + ' ' + user.last_name

        dto = GetAllRegistrationsDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            registration_date=datetime.strftime(attendee.registration_timestamp.date(), '%d-%m-%Y'),
            registered_by=user_name,
            event_name=event.event_title if event else None
        )
        return_dto.append(dto)

    return {"status": 200, "message": "All Events fetched successfully", "body": return_dto}

@app.get("/all_inactive_events")
def get_inactive_events(db : db_dependency):
    result = db.query(Attendee_Bkp).filter(Attendee_Bkp.reg_status == 'inactive').all()
    print(len(result))

    return_dto: List[GetAllRegistrationsDTO] = []

    for attendee in result:
        
        event = db.query(EventBackUp).filter(EventBackUp.event_id == attendee.event_id).first()
        user = db.query(User).filter(User.user_id == attendee.user_id).first()

        user_name = user.first_name
        if user.last_name:
            user_name = user_name + ' ' + user.last_name

        dto = GetAllRegistrationsDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            registration_date=datetime.strftime(attendee.registration_timestamp.date(), '%d-%m-%Y'),
            registered_by=user_name,
            event_name=event.event_title if event else None
        )
        return_dto.append(dto)

    return {"status": 200, "message": "All Inactive Events fetched successfully", "body": return_dto}

@app.on_event("shutdown")
def shutdown_event():
    db: Session = next(get_db())
    try:
        records_to_update = db.query(UserLog).filter(UserLog.logout_tstmp.is_(None)).all()
        
        for record in records_to_update:
            record.logout_tstmp = datetime.now()
        
        db.commit()
    except Exception as e:
        db.rollback()  # Rollback in case of any errors
        print(f"Error during shutdown event: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000", "http://localhost:5000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)