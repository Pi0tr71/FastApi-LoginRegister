from functools import wraps
import schemas
import models
from models import User
from database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth_bearer import JWTBearer
from utils import create_access_token, create_refresh_token, verify_password, get_hashed_password
from datetime import datetime
from models import TokenTable
from auth_bearer import decodeJWT
import uvicorn
import webbrowser

# Tworzymy bazę danych
Base.metadata.create_all(engine)


# Funkcja zwracająca sesję do bazy danych
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Inicjalizacja aplikacji FastAPI
app = FastAPI()


# Endpoint do rejestracji użytkownika
@app.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    # Sprawdzamy, czy żadne z pól nie są puste
    if any(value == "" for value in [user.email, user.firstname, user.lastname, user.password, user.username]):
        raise HTTPException(status_code=400,
                            detail="Email, password, and username cannot be None. Please provide valid values for all fields.")
    # Sprawdzamy, czy email już istnieje w bazie danych
    existing_user_email = session.query(models.User).filter_by(email=user.email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Sprawdzamy, czy login już istnieje w bazie danych
    existing_user_login = session.query(models.User).filter_by(email=user.username).first()
    if existing_user_login:
        raise HTTPException(status_code=400, detail="Login already registered")

    # Haszujemy hasło przed zapisem do bazy danych
    encrypted_password = get_hashed_password(user.password)
    new_user = models.User(username=user.username, firstname=user.firstname, lastname=user.lastname, email=user.email,
                           password=encrypted_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


# Endpoint do logowania użytkownika
@app.post('/login', response_model=schemas.TokenSchema)
def login(request: schemas.requestdetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = models.TokenTable(user_id=user.id, access_toke=access, refresh_toke=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }


# Endpoint do zmiany hasła użytkownika
@app.post('/change-password')
def change_password(request: schemas.changepassword, db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    if request.new_password == "":
        raise HTTPException(status_code=400,
                            detail="New password cannot be None.")
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"message": "Password changed successfully"}


# Funkcja dekorująca do sprawdzania tokena JWT
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = decodeJWT(kwargs['dependencies'])
        user_id = payload['sub']
        data = kwargs['db'].query(models.TokenTable).filter_by(user_id=user_id, access_toke=kwargs['dependencies'],
                                                               status=True).first()
        if data:
            return func(**kwargs)
        else:
            return {'message': "Token blocked"}

    return wrapper


# Endpoint do wylogowywania użytkownika
@app.post('/logout')
@token_required
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    payload = decodeJWT(dependencies)
    user_id = payload['sub']
    token_record = db.query(models.TokenTable).all()
    info = []
    for record in token_record:
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()

    existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id,
                                                        models.TokenTable.access_toke == dependencies).first()
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}


# Endpoint do pobierania profilu użytkownika
@app.get('/profile/{username}', response_model=schemas.UserProfile)
def get_profile(username: str, db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    return {"username": user.username, "email": user.email, "firstname": user.firstname, "lastname": user.lastname}


# Endpoint do aktualizacji profilu użytkownika
@app.put("/profile/{username}")
@token_required
def update_profile(username: str, request: schemas.updateprofile, db: Session = Depends(get_session), dependencies=Depends(JWTBearer())):
    if any(value == "" for value in [request.email, request.username, request.firstname, request.lastname]):
        raise HTTPException(status_code=400,
                            detail="Email and username cannot be None. Please provide valid values for all fields.")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    payload = decodeJWT(dependencies)
    user_id = payload['sub']
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user.username == username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    if request.username:
        existing_user_username = db.query(models.User).filter_by(email=request.username).first()
        if existing_user_username:
            raise HTTPException(status_code=400, detail="Username already used")
        user.username = request.username

    if request.email:
        existing_user_email = db.query(models.User).filter_by(email=request.email).first()
        if existing_user_email:
            raise HTTPException(status_code=400, detail="Email already used")
        user.email = request.email

    if request.firstname:
        user.firstname = request.firstname

    if request.lastname:
        user.lastname = request.lastname

    db.commit()
    db.refresh(user)
    return {"username": user.username, "email": user.email, "firstname": user.firstname, "lastname": user.lastname}


if __name__ == "__main__":
    # Uruchomienie aplikacji za pomocą UVicorn na localhost:8000
    webbrowser.open("http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
