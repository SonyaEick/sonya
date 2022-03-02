from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer, DateTime


app = FastAPI()

# ----- DATABASE -----

SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBUser(Base):
    __tablename__ = 'places'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    birth = Column(DateTime)
    category = Column(String, nullable=True)
    notes = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)


# ----- MODELS ------
# Methods for interacting with the database

class User(BaseModel):
    id: int
    name: str
    birth: Optional[datetime.date] = None
    category: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True


def get_user(db: Session, user_id: int):
    return db.query(DBUser).where(DBUser.id == user_id).first()

def get_users(db: Session):
    return db.query(DBUser).all()

def create_user(db: Session, user: User):
    db_user = DBUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def del_user(db: Session, user_id: int):
    user = db.query(DBUser).where(DBUser.id == user_id).first()
    userid, username = user.id, user.name
    db.delete(user)
    db.commit()
    return f'{userid} - {username} has been deleted'


# ----- API ROUTES ------
# Routes for interacting with the API

@app.post('/users/', response_model=User)
def create_users_view(user: User, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user

@app.get('/users/', response_model=List[User])
def get_users_view(db: Session = Depends(get_db)):
    return get_users(db)

@app.get('/user/{user_id}')
def get_user_view(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)


@app.delete('/user/{user_id}')
def del_user_view(user_id: int, db: Session = Depends(get_db)):
    return del_user(db, user_id)


@app.get('/')
async def root():
    return {'message': 'Welcome'}


