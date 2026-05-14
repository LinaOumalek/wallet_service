from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI, status, Depends, JSONResponse
from helper_functions import validate_email_uniqueness, validate_phone_number_uniqueness, validate_user_existence
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import get_db, User
app = FastAPI()

class UserCreate(BaseModel):
    full_name : str = Field(max_length=100)
    email : EmailStr = Field(max_length=255)
    phone_number : str | None = Field(default = None, max_length=15, min_length = 10, regex=r"^[0-9]+$")

class SuccessResponse(BaseModel):
    status : str = "success"
    data : dict | None = None
    code : int = Field(default=200)

class ErrorResponse(BaseModel):
    message = str
    code = int

@app.post("/users", response_model = SuccessResponse, status_code = status.HTTP_201_CREATED)
def create_user(user : UserCreate, db : Session = Depends(get_db)):
    if not validate_email_uniqueness(user.email, db):
        return JSONResponse(status_code = 409, content = ErrorResponse(message = "Email already exists", code = 409).model_dump())
    if user.phone_number and not validate_phone_number_uniqueness(user.phone_number, db):
        return JSONResponse(status_code = 409, content = ErrorResponse(message = "Phone number already exists", code = 409))
    new_user = User(full_name = user.full_name, email = user.email, phone_number = user.phone_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return SuccessResponse(data = {"id": new_user.id, "full_name": user.full_name, "email": user.email, "phone_number": user.phone_number}, code=201)

@app.get("/users/{user_id}", response_model = SuccessResponse, status_code = status.HTTP_200_OK)
def get_user(user_id : int, db : Session = Depends(get_db)):
    if not validate_user_existence(user_id, db):
        return JSONResponse(status_code = 404, content = ErrorResponse(message = "User not found", code = 404))
    
    statement = select(User).where(User.user_id == user_id)
    user = db.scalars(statement).first()
    return SuccessResponse(data = {"user_id": user_id, "full_name": user.full_name, "phone_number": user.phone_number, "wallet(s)": user.wallets})

    