from db import get_db, User
from sqlalchemy.orm import Session
from sqlalchemy import select

def validate_email_uniqueness(email : str, db : Session):
    statement = select(User).where(User.email == email)
    res = db.scalars(statement).first()
    return res is None

def validate_phone_number_uniqueness(phone_number : str, db : Session):
    statement = select(User).where(User.phone_number == phone_number)
    res = db.scalars(statement).first()
    return res is None

def validate_user_existence(user_id : int, db : Session):
    statement = select(User).where(User.user_id == user_id)
    res = db.scalars(statement).first()
    return res is not None