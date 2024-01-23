from pydantic import BaseModel
import datetime


class UserCreate(BaseModel):
    username: str
    firstname: str
    lastname: str
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
    firstname: str
    lastname: str
    username: str
    email: str


class updateprofile(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
