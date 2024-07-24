from fastapi import FastAPI
from database import Base, SessionLocal, engine
from pydantic import BaseModel
import model
from typing import Annotated

app = FastAPI()

model.Base.metadata.create_all(bind = engine)