from fastapi import FastAPI, Depends, BackgroundTasks, status, Request
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal, engine
from dto import UserRegistrationDTO, UserLoginDTO, UserResponseDTO, \
    EventCreateDTO, EventUpdateDTO, RegisterForEvent, \
    GetRegisteredUserDTO, GetUsersForEventDTO, \
    GetAllRegistrationsDTO
from model import Base, User, Event, Attendee, UserLog, EventBackUp, \
    EventOpsLog, Attendee_Bkp
from typing import Annotated, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from auth import get_password_hash, verify_password
import random
import re
from sqlalchemy import func
import utils
import json
from threading import Thread
import logging
import uvicorn
from utils import log_api, raise_validation_error
import requests
import sys
import subprocess

# Create an object for the FastAPI Class
app = FastAPI()

# Implement Logger
formatted_name = f'loggers/app_{datetime.now().strftime("%Y%m%d")}.log'
logging.basicConfig(level=logging.INFO,
                    filename=formatted_name,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the tables provided in metadata
Base.metadata.create_all(bind=engine)


# Create a function to validate the event Date
def validate_event_date(db, request, logger, date_str: str) -> datetime:
    try:
        event_date = datetime.strptime(date_str, '%d-%m-%Y')
    except ValueError:
        raise_validation_error(db, request, 400,
                               "Invalid date format. Use DD-MM-YYYY.", logger)
    if event_date < datetime.now():
        raise_validation_error(db, request, 400,
                               "The event date cannot be in the past.",
                               logger)
    return event_date.date().strftime('%d-%m-%Y')


# Create a function to validate the event Time
def validate_event_time(db, request, logger, time_str: str) -> datetime:
    try:
        event_time = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        raise_validation_error(db, request, 400,
                               "Invalid time format. Use HH:MM.", logger)
    return event_time.strftime('%H:%M')


# Fetch Database and Make a local session as long as we work on database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Set up Database Dependency
db_dependency = Annotated[Session, Depends(get_db)]


# Create a function to clean the older data
def cleanUpOlderData():
    db: Session = next(get_db())
    logger.info("Clean Up Started...")
    curr_date = datetime.now().strftime("%d-%m-%Y")
    inactive_events = db.query(Event).filter(
        func.to_date(Event.date_of_event, 'DD-MM-YYYY') < curr_date
        ).all()
    if len(inactive_events) == 0:
        logger.info("No earlier events to be Cleaned")
    else:
        logger.info(f"Cleaning up {len(inactive_events)} events: ")
        cnt = 1
        for event in inactive_events:
            logger.info(f"{cnt}. {event.event_title} - {event.date_of_event}")

            # Updating the Status in Event Backup table to inactive
            db.query(EventBackUp).filter(
                EventBackUp.event_id == event.event_id
                ).update(
                {EventBackUp.flag: "inactive",
                 EventBackUp.latest_op: "DELETE",
                 EventBackUp.op_tstmp: datetime.now()},
                synchronize_session=False
            )

            # Updating the reg_status for all the events who are cleaned up
            db.query(Attendee_Bkp).filter(
                Attendee_Bkp.event_id == event.event_id
                ).update(
                {Attendee_Bkp.reg_status: "inactive"},
                synchronize_session=False
            )

            # Adding the Delete Log to the Event Operations
            log_obj = EventOpsLog(
                event_id=event.event_id,
                op_type="DELETE",
                op_desc="This Event is expired and hence cleaned up",
                op_tstmp=datetime.now())
            db.add(log_obj)
            db.delete(event)
            db.commit()
            cnt += 1
        logger.info("Clean-Up Completed")


# This is the function used by thread to send recommended mails
def trigger_email():
    while True:
        if datetime.now().time().strftime('%H:%M:%S') == "12:00:00":
            requests.get("http://127.0.0.1:8083/daily_recom")


# This is a thread that keeps running as long as server is running
def start_background_task():

    task_thread = Thread(target=cleanUpOlderData)
    task_thread.daemon = True
    task_thread.start()

    task_thread = Thread(target=trigger_email)
    task_thread.daemon = True
    task_thread.start()


# This function is called immediately after the backend starts running
@app.on_event("startup")
async def startup_event():
    logger.info("Backend Started..!")
    start_background_task()


# -#-#-#-#-# USER API #-#-#-#-#- #
# Create a Registration Function that posts to database
@app.post("/user/register", status_code=201)
def register_user(user_obj: UserRegistrationDTO, request: Request,
                  db: db_dependency, background_tasks: BackgroundTasks):
    logger.info("Endpoint Accessed - 'POST /user/register'")
    if db.query(User).filter(
        func.lower(User.email) == user_obj.email.strip().lower()
            ).first():
        raise_validation_error(db, request, 400,
                               "User with the same email already exists",
                               logger)
    if not user_obj.email or not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            user_obj.email):
        raise_validation_error(db, request, 400,
                               "Invalid or missing email", logger)
    if not user_obj.phone or len(user_obj.phone) < 10:
        raise_validation_error(db, request, 400,
                               "Invalid or missing phone number", logger)
    if not user_obj.first_name.strip():
        raise_validation_error(db, request, 400,
                               "First Name is mandatory", logger)
    if not user_obj.password or len(user_obj.password.strip()) < 7:
        raise_validation_error(db, request, 400,
                               "Password must be at least 7 characters",
                               logger)
    if not re.match(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@#$%^&+=]+$",
            user_obj.password):
        raise_validation_error(
            db, request, 400,
            (
                "Weak password: Use a combination of uppercase, "
                "lowercase, and numbers"
            ),
            logger)
    encrypted_pwd = get_password_hash(user_obj.password)

    # Create new user object
    new_user = User(
        first_name=user_obj.first_name.strip(),
        last_name=user_obj.last_name.strip() if user_obj.last_name else None,
        email=user_obj.email.strip(),
        password=encrypted_pwd,
        registered_date=datetime.now(),
        phone=user_obj.phone.strip()
    )

    # Add user to the database
    db.add(new_user)
    db.commit()
    log_api(db, request, status.HTTP_201_CREATED,
            "User Successfully Registered", log=logger)

    # Send a registration email in the background
    user_name = f"{new_user.first_name} {new_user.last_name}".strip()
    background_tasks.add_task(utils.registration_email, new_user.email,
                              user_name)

    return {"status_code": 201, "message": "User Successfully Registered"}


# This API is used to login to session
@app.post("/user/login", status_code=200)
def login_user(user_login_obj: UserLoginDTO, db: db_dependency,
               request: Request):
    logger.info("Endpoint Accessed - 'POST /user/login'")
    db_user = db.query(User).filter(
        User.email == user_login_obj.email
        ).first()

    if not db_user:
        raise_validation_error(db, request, 401,
                               "Unregistered Email", logger)
    if not verify_password(user_login_obj.password, db_user.password):
        raise_validation_error(db, request, 401,
                               "Invalid Credentials", logger)
    if db_user.last_name is None:
        db_user.last_name = ""

    db.query(UserLog).filter(
        UserLog.user_id == db_user.user_id,
        UserLog.logout_tstmp is None
        ).update(
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
    log_api(db, request, status.HTTP_200_OK,
            "Successfully Logged in..!", log=logger)
    return {"status_code": 200,
            "message": "Successfully Logged in..!",
            "body": user_passon_dto}


# This API helps to maintain the LOG OUT Tracking
@app.put("/user/logout/{log_id}")
def logout_user(log_id: int, request: Request, db: db_dependency):

    logger.info("Endpoint Accessed - 'PUT /user/logout'")
    user_obj = db.query(UserLog).filter(UserLog.log_id == log_id).first()
    if user_obj is None:
        raise_validation_error(db, request, 401,
                               "No Active Session found", logger)
    user_obj.logout_tstmp = datetime.now()
    db.commit()
    log_api(db, request, status.HTTP_200_OK,
            "Successfully Logged Out", logger)
    return {"status_code": 200, "message": "Suceessfully Logged out"}


# -#-#-#-#-# EVENT API #-#-#-#-#- #
# Create Event Function
@app.post("/create-event", status_code=201)
def create_event(create_event_obj: EventCreateDTO, request: Request,
                 db: db_dependency):

    logger.info("Endpoint Accessed - 'POST /create-event'")
    event_date = validate_event_date(db, request, logger,
                                     create_event_obj.date_of_event)
    event_time = validate_event_time(db, request, logger,
                                     create_event_obj.time_of_event)
    db_user = db.query(User).filter(
        create_event_obj.organizer_id == User.user_id
        ).first()
    if not db_user:
        raise_validation_error(db, request, 404,
                               "User has no previlege to organize event",
                               logger)
    if len(create_event_obj.event_title.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Event Title is mandatory", logger)
    if len(create_event_obj.event_description.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Event Description is mandatory", logger)
    if len(create_event_obj.time_of_event.strip()) == 0:
        raise_validation_error(db, request, 400, "Time is mandatory", logger)
    if (len(create_event_obj.location.strip()) == 0):
        raise_validation_error(db, request, 400,
                               "Location can not be empty", logger)
    if not create_event_obj.capacity:
        raise_validation_error(db, request, 400,
                               "Capacity can not be empty", logger)
    elif create_event_obj.capacity <= 0:
        raise_validation_error(db, request, 400,
                               "Capacity can not be zero or invalid", logger)
    e_title = db.query(Event).filter(
        Event.event_title == create_event_obj.event_title
        ).first()
    if e_title is not None:
        raise_validation_error(db, request, 409,
                               "Event Name already Exists..!", logger)
    event_dt = create_event_obj.date_of_event
    event_tm = create_event_obj.time_of_event
    if create_event_obj.location.lower() != "online":
        event_datetime = datetime.strptime(
            f"{event_dt} {event_tm}", '%d-%m-%Y %H:%M'
        )
        start_time_window = event_datetime - timedelta(hours=3)
        end_time_window = event_datetime + timedelta(hours=3)

        conflicting_event = db.query(Event).filter(
            Event.date_of_event == event_date,
            Event.location == create_event_obj.location.lower(),
            Event.time_of_event.between(
                start_time_window.time().strftime('%H:%M'),
                end_time_window.time().strftime('%H:%M')
                )
        ).first()
        if conflicting_event is not None:
            raise_validation_error(
                db, request, 409,
                "Unable to register since there is a conflicting event.",
                logger)

    if db_user.privilege == "USER":
        event_create_dto = Event(
            event_title=create_event_obj.event_title,
            event_description=create_event_obj.event_description,
            time_of_event=event_time,
            date_of_event=event_date,
            organizer_id=create_event_obj.organizer_id,
            location=create_event_obj.location.lower(),
            capacity=create_event_obj.capacity,
            request_timestamp=datetime.now()
            )
    else:
        event_create_dto = Event(
            event_title=create_event_obj.event_title,
            event_description=create_event_obj.event_description,
            time_of_event=event_time,
            date_of_event=event_date,
            organizer_id=create_event_obj.organizer_id,
            location=create_event_obj.location.lower(),
            capacity=create_event_obj.capacity,
            request_timestamp=datetime.now(),
            approved_timestamp=datetime.now(),
            status='approved'
            )
    db.add(event_create_dto)
    db.commit()

    x = json.dumps(create_event_obj.dict())
    res = db.query(Event).filter(
        Event.event_title == event_create_dto.event_title
        ).first()
    event_bkp_dto = EventBackUp(
                        event_id=res.event_id,
                        event_title=res.event_title,
                        event_description=res.event_description,
                        time_of_event=res.time_of_event,
                        date_of_event=res.date_of_event,
                        organizer_id=res.organizer_id,
                        location=res.location,
                        capacity=res.capacity,
                        request_timestamp=res.request_timestamp,
                        approved_timestamp=res.approved_timestamp,
                        status=res.status,
                        latest_op='POST',
                        op_tstmp=datetime.now()
                        )
    log_obj = EventOpsLog(
        event_id=res.event_id,
        op_type="POST",
        op_desc=x + " is added",
        op_tstmp=datetime.now())
    db.add(event_bkp_dto)
    db.add(log_obj)
    db.commit()
    log_api(db, request, status.HTTP_201_CREATED,
            "Event successfully created", log=logger)
    return {"status_code": 201, "message": "Event successfully created"}


# This API is used to update the existing event
@app.put("/event/{event_id}")
def update_event(update_event_obj: EventUpdateDTO,
                 event_id: int, db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'PUT /event/{event_id}'")
    result = db.query(Event).filter(Event.event_id == event_id).first()
    result_bkp = db.query(EventBackUp).filter(
        EventBackUp.event_id == event_id
        ).first()
    update_dict = update_event_obj.dict()
    result_dict = {key: value for key, value in result.__dict__.items()
                   if not key.startswith('_')}
    changes = []
    for key, update_value in update_dict.items():
        result_value = result_dict.get(key)
        if update_value != result_value:
            changes.append(
                f"{key} changed from {result_value} to {update_value}"
                )

    # Prepare the message
    if changes:
        message = ", ".join(changes)
    else:
        message = "No Changes Done"

    logger.info(message)
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No event with id: {event_id}", logger)
    event_date = validate_event_date(db, request, logger,
                                     update_event_obj.date_of_event)
    event_time = validate_event_time(db, request, logger,
                                     update_event_obj.time_of_event)
    db_user = db.query(User).filter(
        update_event_obj.organizer_id == User.user_id
        ).first()
    if not db_user:
        raise_validation_error(db, request, 404,
                               "User has no privilege to organize event",
                               logger)
    if len(update_event_obj.event_title.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Event Title is mandatory", logger)
    if len(update_event_obj.event_description.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Event Description is mandatory", logger)
    if len(update_event_obj.time_of_event.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Time is mandatory", logger)
    if len(update_event_obj.location.strip()) == 0:
        raise_validation_error(db, request, 400,
                               "Location cannot be empty", logger)
    e_title = db.query(Event).filter(
        Event.event_title == update_event_obj.event_title,
        Event.event_id != event_id
    ).first()
    if e_title is not None:
        raise_validation_error(db, request, 409,
                               "Event Name already Exists..!", logger)

    update_dt = update_event_obj.date_of_event
    update_tm = update_event_obj.time_of_event
    # If it is online, Can allow multiple Events
    if update_event_obj.location != "online":
        event_datetime = datetime.strptime(
            f"{update_dt} {update_tm}", '%d-%m-%Y %H:%M')
        start_time_window = event_datetime - timedelta(hours=3)
        end_time_window = event_datetime + timedelta(hours=3)
        conflicting_event = db.query(Event).filter(
            Event.date_of_event == event_date,
            Event.location == update_event_obj.location.lower(),
            Event.event_id != event_id,
            Event.time_of_event.between(
                start_time_window.time().strftime('%H:%M'),
                end_time_window.time().strftime('%H:%M')
                )
        ).first()
        if conflicting_event is not None:
            raise_validation_error(
                db, request, 409,
                "Unable to update since there is a conflicting event.",
                logger)

    # Update the existing event with the new data
    result_bkp.event_id = event_id
    result.event_title = result_bkp.event_title = update_event_obj.event_title
    result.event_description = update_event_obj.event_description
    result_bkp.event_description = update_event_obj.event_description
    result.time_of_event = result_bkp.time_of_event = event_time
    result.date_of_event = result_bkp.date_of_event = event_date
    result.organizer_id = update_event_obj.organizer_id
    result_bkp.organizer_id = update_event_obj.organizer_id
    result.location = update_event_obj.location.lower()
    result_bkp.location = update_event_obj.location.lower()
    result.capacity = update_event_obj.capacity
    result_bkp.capacity = update_event_obj.capacity
    result.request_timestamp = result_bkp.request_timestamp = datetime.now()
    result.status = result_bkp.status = 'pending'
    result_bkp.latest_op = 'PUT'
    result_bkp.op_tstmp = datetime.now()

    if db_user.privilege != "USER":
        result.approved_timestamp = \
            result_bkp.approved_timestamp = datetime.now()
        result.status = result_bkp.status = 'approved'
    log_obj = EventOpsLog(
        event_id=event_id, op_type="PUT",
        op_desc=message, op_tstmp=datetime.now()
        )
    db.add(log_obj)
    db.commit()
    log_api(db, request, status.HTTP_200_OK,
            f"Event with id: {event_id} successfully updated", log=logger)
    return {"status_code": 200, "message": "Event successfully updated"}


# This API Gets All Events
@app.get("/all-events")
def get_all_events(db: db_dependency, request: Request):
    logger.info("Endpoint Accessed - 'GET /all-events'")
    log_api(db, request, status.HTTP_200_OK, "All Events Fetched", log=logger)
    result = db.query(Event).all()
    return {"status_code": 200, "body": result}


# This API returns all the pending events
@app.get("/pending-events")
def get_pending_events(db: db_dependency, request: Request):
    logger.info("Endpoint Accessed - 'GET /pending-events'")
    log_api(db, request, status.HTTP_200_OK,
            "Pending Events fetched", log=logger)
    result = db.query(Event).filter(Event.status == "pending").all()
    return {"status_code": 200, "body": result}


# This API returns only approved events
@app.get("/approved-events")
def get_approved_events(db: db_dependency, request: Request):
    logger.info("Endpoint Accessed - 'GET /approved-events'")
    log_api(db, request, status.HTTP_200_OK,
            "Approved Events fetched", log=logger)
    date_to_show = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    result = db.query(Event).filter(
        Event.status == "approved",
        func.to_date(Event.date_of_event, 'DD-MM-YYYY') >= date_to_show
        ).all()
    return {"status_code": 200, "body": result}


# This event returns the Available events
@app.get("/available-events/{user_id}")
def get_available_events(user_id: int, db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'GET /available-events/{user_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Available Events fetched for User: {user_id}", log=logger)
    date_to_show = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    result = db.query(Event).filter(
        Event.status == "approved",
        Event.organizer_id != user_id,
        func.to_date(Event.date_of_event, 'DD-MM-YYYY') >= date_to_show
        ).all()
    return {"status_code": 200, "body": result}


# This API is used to delete the event
@app.delete("/delete-event/{event_id}")
def delete_event(event_id: int, db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'DELETE /delete-events/{event_id}'")
    db.query(EventBackUp).filter(EventBackUp.event_id == event_id).update(
        {EventBackUp.flag: "inactive",
         EventBackUp.latest_op: "DELETE",
         EventBackUp.op_tstmp: datetime.now()},
        synchronize_session=False
    )
    db.query(Attendee_Bkp).filter(Attendee_Bkp.event_id == event_id).update(
        {Attendee_Bkp.reg_status: "inactive"},
        synchronize_session=False
    )
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No Event found with id: {event_id}", logger)
    db.delete(result)
    log_obj = EventOpsLog(event_id=event_id, op_type="DELETE",
                          op_desc="This Event is Deleted",
                          op_tstmp=datetime.now())
    db.add(log_obj)
    db.commit()
    log_api(db, request, status.HTTP_200_OK,
            f"Event with Event_id: {event_id} Deleted", log=logger)
    return {"status_code": 200, "message": "Event deleted Successfully"}


# This API gets event by event_id
@app.get("/event/{event_id}")
def get_event_by_id(event_id: int, db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'GET /event/{event_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Fetching Event: {event_id}", logger)
    result = db.query(Event).filter(Event.event_id == event_id).first()
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No Event found with id: {event_id}", logger)
    return {"status_code": 200, "body": result}


# This API gets all events of a user
@app.get("/event_by_user/{user_id}")
def get_event_by_user_id(user_id: int, db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'GET /event_by_user/{user_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Fetching Event for user: {user_id}", logger)
    result = db.query(Event).filter(Event.organizer_id == user_id).all()
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No event organised by user: {user_id}",
                               logger)
    return {"status_code": 200, "body": result}


# This API gets each pending event of a specific User
@app.get("/event_by_user/pending/{user_id}")
def get_pending_event_by_user_id(user_id: int, db: db_dependency,
                                 request: Request):
    logger.info(f"Endpoint Accessed - 'GET /event_by_user/pending/{user_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Pending Events fetching for user: {user_id}", logger)
    result = db.query(Event).filter(
        Event.organizer_id == user_id
        ).filter(Event.status == "pending").all()
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No event organised by user: {user_id}",
                               logger)
    return {"status_code": 200, "body": result}


# This API approves individual Events
@app.put("/approve-event/{event_id}")
def approve_event(event_id: int, db: db_dependency,
                  background_tasks: BackgroundTasks,
                  request: Request):
    logger.info(f"Endpoint Accessed - 'PUT /approve-event/{event_id}'")
    result = db.query(Event).filter(Event.event_id == event_id).first()
    result_bkp = db.query(EventBackUp).filter(
        EventBackUp.event_id == event_id
        ).first()
    if result is None:
        raise_validation_error(db, request, 404,
                               f"No event with id: {event_id}", logger)
    if result.status == "approved":
        raise_validation_error(db, request, 409,
                               "This event is already approved", logger)
    result.approved_timestamp = result_bkp.approved_timestamp = datetime.now()
    result.status = result_bkp.status = "approved"
    log_obj = EventOpsLog(event_id=event_id, op_type="PUT",
                          op_desc="Your event got approved by admin",
                          op_tstmp=datetime.now())
    db.add(log_obj)
    user = db.query(User).filter(result.organizer_id == User.user_id).first()
    user_name = user.first_name + " " + user.last_name \
        if user.last_name is not None else user.first_name
    background_tasks.add_task(
        utils.approval_email, user_name, result.event_title,
        result.date_of_event, result.time_of_event, result.location,
        result.event_description, user.email
        )
    db.commit()
    log_api(db, request, status.HTTP_200_OK,
            f"Event with event Id: {event_id} Approved ", logger)
    return {"status_code": 200, "message": "event approved"}


# This API approves all the events
@app.put("/approve-all-events")
def approve_all_event(db: db_dependency,
                      background_tasks: BackgroundTasks, request: Request):
    logger.info(f"Endpoint Accessed - 'PUT /approve-all-events'")
    result = db.query(Event).filter(
        Event.status == "pending"
        ).all()
    result_bkp = db.query(EventBackUp).filter(
        EventBackUp.status == "pending"
        ).all()
    for i in result:
        i.approved_timestamp = datetime.now()
        i.status = "approved"
        user = db.query(User).filter(i.organizer_id == User.user_id).first()
        user_name = user.first_name + " " + user.last_name\
            if user.last_name is not None else user.first_name
        background_tasks.add_task(
            utils.approval_email, user_name, i.event_title, i.date_of_event,
            i.time_of_event, i.location, i.event_description, user.email
            )
        db.commit()
    for i in result_bkp:
        i.approved_timestamp = datetime.now()
        i.status = "approved"
        log_obj = EventOpsLog(event_id=i.event_id, op_type="PUT",
                              op_desc="Your event got approved by admin",
                              op_tstmp=datetime.now())
        db.add(log_obj)
        db.commit()
        log_api(db, request, status.HTTP_200_OK,
                f"Event with event Id: {i.event_id} Approved ", logger)
    return {"status_code": 200, "message": "events approved"}


# -#-#-#-#-# REGISTRATIONS API #-#-#-#-#- #
# This API is used to register for an event
@app.post("/register_event", status_code=201)
def register_for_event(reg_dto: RegisterForEvent,
                       db: db_dependency,
                       background_tasks: BackgroundTasks, request: Request):
    logger.info(f"Endpoint Accessed - 'POST /register_event'")
    user_check = db.query(User).filter(
        User.user_id == reg_dto.user_id
        ).first()
    if user_check is None:
        raise_validation_error(
            db, request, 404,
            f"User with User ID: {reg_dto.user_id} does not exist", logger
            )
    event_check = db.query(Event).filter(
        Event.event_id == reg_dto.event_id
        ).first()
    if event_check is None:
        raise_validation_error(
            db, request, 404,
            f"Event with Event ID: {reg_dto.event_id} does not exist", logger
            )
    elif event_check.status != 'approved':
        raise_validation_error(
            db, request, 409,
            "Unable to register since Event is not yet approved", logger
            )
    elif event_check.organizer_id == reg_dto.user_id:
        raise_validation_error(db, request, 409,
                               "Cannot register since user is organizer",
                               logger)

    # Check if the email is already registered for the same event
    email_check = db.query(Attendee).filter(
        Attendee.email == reg_dto.email,
        Attendee.event_id == reg_dto.event_id
        ).first()
    if email_check is not None:
        if email_check.users.privilege == "ADMIN":
            raise_validation_error(
                db, request, 409,
                "Oops. Admin is blocked from Registration.!", logger
                )
        raise_validation_error(db, request, 409,
                               "Email already registered for this event",
                               logger)
    event_count = db.query(Attendee).filter(
        Attendee.event_id == reg_dto.event_id
        ).count()
    if event_count >= event_check.capacity:
        raise_validation_error(db, request, 409,
                               "Cannot register since max Capacity reached",
                               logger)
    if not reg_dto.email.strip():
        raise_validation_error(db, request, 400,
                               "Email cannot be empty", logger)
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    reg_dto.email):
        raise_validation_error(db, request, 400,
                               "Invalid Email Format", logger)
    if reg_dto.phone:
        if len(reg_dto.phone) < 10:
            raise_validation_error(
                db,
                request, 400,
                "Phone Number should not be less than 10 digits", logger
                )
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
    background_tasks.add_task(utils.gratitude_email,
                              reg_dto.attendee_name, event_check.event_title,
                              event_check.date_of_event,
                              event_check.time_of_event,
                              event_check.location,
                              event_check.event_description, reg_dto.email)
    db.commit()
    log_api(db, request, status.HTTP_200_OK,
            "Registered for the event successfully", logger)
    return {"status_code": 201,
            "message": "Registered for the event successfully"}


# This API is used to get registered events by user id
@app.get("/registered_event/users/{user_id}")
def get_registered_events_by_user_id(user_id: int, db: db_dependency,
                                     request: Request):
    logger.info(f"Endpoint Accessed - 'GET /registered_event/"
                "users/{user_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Registered Events fetched for User: {user_id}", log=logger)
    result = db.query(Attendee).filter(Attendee.user_id == user_id).all()
    return_dto: List[GetRegisteredUserDTO] = []

    for attendee in result:
        event = db.query(Event).filter(
            Event.event_id == attendee.event_id
            ).first()
        dto = GetRegisteredUserDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            event_name=event.event_title if event else None,
            event_description=event.event_description,
            time_of_event=event.time_of_event,
            date_of_event=event.date_of_event,
            location=event.location,
            registration_date=datetime.strftime(
                attendee.registration_timestamp.date(),
                '%d-%m-%Y'
                )
        )
        return_dto.append(dto)
    return {"status": 200,
            "message": "Events fetched successfully",
            "body": return_dto}


# API Call to get registered_events for an event
@app.get("/registered_event/events/{event_id}")
def get_registered_events_by_event_id(event_id: int, db: db_dependency,
                                      request: Request):
    logger.info(f"Endpoint Accessed - 'GET /registered_event/"
                "events/{event_id}'")
    log_api(db, request, status.HTTP_200_OK,
            f"Registrations fetched for EVENT: {event_id}", logger)
    result = db.query(Attendee).filter(Attendee.event_id == event_id).all()
    return_dto: List[GetUsersForEventDTO] = [
        GetUsersForEventDTO(attendee_name=attendee.attendee_name,
                            email=attendee.email,
                            phone=attendee.phone,
                            registration_date=datetime.strftime(
                                attendee.registration_timestamp.date(),
                                '%d-%m-%Y'
                                )) for attendee in result
    ]
    return {"status": 200,
            "message": "Registrations fetched successfully",
            "body": return_dto}


# API call to return all registered events
@app.get("/all_registered_events")
def get_all_registered_events(db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'GET /all_registered_events'")
    log_api(db, request, status.HTTP_200_OK, f"All Registrations fetched",
            logger)
    result = db.query(Attendee).all()
    return_dto: List[GetAllRegistrationsDTO] = []

    for attendee in result:
        event = db.query(Event).filter(
            Event.event_id == attendee.event_id
            ).first()
        user = db.query(User).filter(
            User.user_id == attendee.user_id
            ).first()
        user_name = user.first_name
        if user.last_name:
            user_name = user_name + ' ' + user.last_name
        dto = GetAllRegistrationsDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            registration_date=datetime.strftime(
                attendee.registration_timestamp.date(), '%d-%m-%Y'
                ),
            registered_by=user_name,
            event_name=event.event_title if event else None
        )
        return_dto.append(dto)
    return {"status": 200,
            "message": "All Events fetched successfully",
            "body": return_dto}


# API Call to get Inactive events
@app.get("/all_inactive_events")
def get_inactive_events(db: db_dependency, request: Request):
    logger.info(f"Endpoint Accessed - 'GET /all_inactive_events'")
    log_api(db, request, status.HTTP_200_OK, f"All Inactive Events fetched",
            log=logger)
    result = db.query(Attendee_Bkp).filter(
        Attendee_Bkp.reg_status == 'inactive'
        ).all()
    return_dto: List[GetAllRegistrationsDTO] = []

    for attendee in result:
        event = db.query(EventBackUp).filter(
            EventBackUp.event_id == attendee.event_id
            ).first()
        user = db.query(User).filter(
            User.user_id == attendee.user_id
            ).first()
        user_name = user.first_name
        if user.last_name:
            user_name = user_name + ' ' + user.last_name
        dto = GetAllRegistrationsDTO(
            attendee_name=attendee.attendee_name,
            email=attendee.email,
            phone=attendee.phone,
            registration_date=datetime.strftime(
                attendee.registration_timestamp.date(), '%d-%m-%Y'
                ),
            registered_by=user_name,
            event_name=event.event_title if event else None
        )
        return_dto.append(dto)
    return {"status": 200,
            "message": "All Inactive Events fetched successfully",
            "body": return_dto}


# GET Call to trigger recommendation of events
@app.get("/daily_recom")
async def recommend_event(db: db_dependency):
    logger.info("Emails Trigger started..!")
    users = db.query(User).all()
    emails = db.query(Attendee_Bkp).all()
    dict1 = dict(
        set([(str(i.email).lower(), str(i.first_name)) for i in users
            if i.privilege == 'USER'] +
            [(str(j.email).lower(), str(j.attendee_name)) for j in emails])
    )
    for email, name in dict1.items():
        event_id = random.choice([
                j.event_id for j in db.query(Event).filter(
                    Event.status == 'approved'
                ).all()
            ])
        event = db.query(Event).filter(Event.event_id == event_id).first()
        utils.recommended_events(email, name, event.event_title,
                                 event.event_description, event.date_of_event,
                                 event.time_of_event)
        logger.info(f"Email sent to {email}")
    logger.info("All the emails are sent")
    return {"status_code": 200,
            "response": "All the emails are sent"}


# Function to be executed just before shutdown
@app.on_event("shutdown")
def shutdown_event():
    db: Session = next(get_db())
    try:
        records_to_update = db.query(UserLog).filter(
            UserLog.logout_tstmp.is_(None)
            ).all()
        for record in records_to_update:
            record.logout_tstmp = datetime.now()
        db.commit()
        logger.info("Backend Shut Down..!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during shutdown event: {e}")


# Allowing CORS Origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ecexute Style Checker before running the Backend
def run_pycodestyle():
    # Run pycodestyle on the app.py file
    result = subprocess.run(["pycodestyle", "main.py"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Code style violations found:\n")
        print(result.stdout)
        logger.warning("Code style violations found:")
        logger.warning(result.stdout)
        # Exit if there are style violations
        sys.exit(1)
    else:
        logger.info("No Check Style error found. Code is Clean")


# Execution of Main Function in target file
if __name__ == "__main__":
    run_pycodestyle()
    uvicorn.run(app, port=8083)
