from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from main import get_session, register_user, login, change_password, logout, get_profile, update_profile
import schemas

app = FastAPI()

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/", response_class=HTMLResponse)
def home(request: HTMLResponse):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register(request: HTMLResponse, user: schemas.UserCreate, session: Session = Depends(get_session)):
    try:
        register_user(user, session)
        message = "Registration successful"
    except HTTPException as e:
        message = f"Registration failed: {e.detail}"

    return templates.TemplateResponse("message.html", {"request": request, "message": message})

@app.post("/login", response_class=HTMLResponse)
def user_login(request: HTMLResponse, email: str, password: str):
    try:
        token = login(schemas.requestdetails(email=email, password=password), get_session())
        message = "Login successful"
    except HTTPException as e:
        token = None
        message = f"Login failed: {e.detail}"

    return templates.TemplateResponse("message.html", {"request": request, "message": message, "token": token})

# Dodaj obsługę pozostałych endpointów (change_password, logout, get_profile, update_profile) w sposób podobny.
# Zdefiniuj odpowiednie szablony HTML dla tych endpointów.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
