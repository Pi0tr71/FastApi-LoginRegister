from typing import Optional
from pydantic import BaseModel
import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class requestdetails(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class changepassword(BaseModel):
    email: str
    old_password: str
    new_password: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime


class UserProfile(BaseModel):
    id: int
    username: str
    email: str


class updateprofile(BaseModel):
    username: Optional[str]
    email: Optional[str]
