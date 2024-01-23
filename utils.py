from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
import bcrypt

# Czas ważności tokena dostępowego (w minutach)
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minut
# Czas ważności tokena odświeżającego (w minutach)
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dni
# Algorytm używany do podpisywania i weryfikacji tokenów JWT
ALGORITHM = "HS256"
# Tajny klucz do podpisywania i weryfikacji tokenów dostępowych
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"  # powinien być tajny
# Tajny klucz do podpisywania i weryfikacji tokenów odświeżających
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

# Funkcja generująca zahashowane hasło
def get_hashed_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    return bcrypt.hashpw(password_bytes, salt)

# Funkcja weryfikująca hasło
def verify_password(password: str, hashed_pass) -> bool:
    password = password.encode('utf-8')
    return bcrypt.checkpw(password, hashed_pass)

# Funkcja generująca token dostępowy
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt

# Funkcja generująca token odświeżający
def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt
