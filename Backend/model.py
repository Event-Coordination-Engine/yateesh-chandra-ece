from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Create a class User to map it as a relation in Database
class User(Base):
    
    __tablename__ = "user"

    user_id = Column(Integer, primary_key = True)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = True)
    email = Column(String, nullable= False)
    password = Column(String, nullable = False)
    phone = Column(String, nullable = False)
    privilege = Column(String, nullable = False, default='USER')
    registered_date = Column(DateTime, nullable = False, default= datetime.now())

    attendees = relationship('Attendee', back_populates='users')
    user_event = relationship('Event', back_populates='organizer')

# Create a class Event to map it as a relation
class Event(Base) :

    __tablename__ = "event"

    event_id = Column(Integer, primary_key = True)
    event_title = Column(String, nullable = False)
    event_description = Column(Text, nullable = False)
    time_of_event = Column(String, nullable = False)
    date_of_event = Column(String, nullable = False)
    organizer_id = Column(Integer, ForeignKey('user.user_id'), nullable= False)
    location = Column(String, nullable = False)
    capacity = Column(Integer, nullable = False)
    request_timestamp = Column(DateTime, nullable = False, default = datetime.now())
    approved_timestamp = Column(DateTime, nullable = True)
    status = Column(String, nullable = False, default = 'pending')

    event_attendee = relationship('Attendee', back_populates='events', cascade = "all, delete-orphan")
    organizer = relationship('User', back_populates='user_event')

# Create a class Attendee to map it as a relation
class Attendee(Base) : 

    __tablename__ = "attendee"

    attendance_sno = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    attendee_name = Column(String, nullable = False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey('event.event_id'), nullable = False)
    registration_timestamp = Column(DateTime, nullable=False, default=datetime.now())

    events = relationship('Event', back_populates='event_attendee')
    users = relationship('User', back_populates='attendees')

class Attendee_Bkp(Base) :
    __tablename__ = "attendee_bkp"

    reg_sno = Column(Integer, primary_key = True)
    user_id = Column(Integer, nullable=False)
    attendee_name = Column(String, nullable = False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    event_id = Column(Integer,ForeignKey('event.event_id', ondelete='CASCADE'))
    registration_timestamp = Column(DateTime, nullable=True, default=datetime.now())
    reg_status = Column(String, nullable = False)

# Create a User Log Relation
class UserLog(Base):
    
    __tablename__ = "user_log"

    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable = False)
    login_tstmp = Column(DateTime, nullable = False, default= datetime.now())
    logout_tstmp = Column(DateTime, nullable= True)

# Create a Backup Table for event such that Even after the Event is deleted, It stays here in Backup
class EventBackUp(Base) :

    __tablename__ = "event_bkp"

    event_bkp_gid = Column(Integer, primary_key = True)
    event_id = Column(Integer, nullable=False)
    event_title = Column(String, nullable = False)
    event_description = Column(Text, nullable = False)
    time_of_event = Column(String, nullable = False)
    date_of_event = Column(String, nullable = False)
    organizer_id = Column(Integer, nullable= False)
    location = Column(String, nullable = False)
    capacity = Column(Integer, nullable = False)
    request_timestamp = Column(DateTime, nullable = False)
    approved_timestamp = Column(DateTime, nullable = True)
    status = Column(String, nullable = False)
    latest_op = Column(String, nullable = False)
    op_tstmp = Column(DateTime, nullable = False, default=datetime.now())
    flag = Column(String, nullable = False, default="active")

class EventOpsLog(Base):

    __tablename__ = "event_ops_log"

    op_gid = Column(Integer, primary_key = True)
    event_id = Column(Integer, nullable=False)
    op_type = Column(String, nullable=False)
    op_desc = Column(String, nullable=False)
    op_tstmp = Column(DateTime, nullable = False, default=datetime.now())

class Api_Audit(Base) :
    
    __tablename__ = "api_audit"

    api_log_id = Column(Integer, primary_key = True)
    api_method = Column(String, nullable = False)
    api_endpoint = Column(String, nullable = False)
    status_code = Column(String, nullable = False)
    response_message = Column(String, nullable = False)
    operation_timestamp = Column(DateTime, nullable = False, default = datetime.now())