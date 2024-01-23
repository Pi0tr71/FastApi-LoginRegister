import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Czas ważności tokena dostępowego
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minut
# Czas ważności tokena odświeżającego
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dni
# Algorytm używany do podpisywania tokenów
ALGORITHM = "HS256"
# Tajny klucz do podpisywania i weryfikacji tokenów dostępowych
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"  # powinien być tajny
# Tajny klucz do podpisywania i weryfikacji tokenów odświeżających
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

# Funkcja do dekodowania tokena JWT
def decodeJWT(jwtoken: str):
    try:
        # Dekoduj i zweryfikuj token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None

# Klasa do obsługi tokena JWT jako nagłówka HTTP
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Nieprawidłowy schemat uwierzytelniania.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Nieprawidłowy token lub wygasły token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Nieprawidłowy kod autoryzacji.")

    # Funkcja do weryfikacji tokena JWT
    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid

# Obiekt do obsługi uwierzytelniania za pomocą tokena JWT
jwt_bearer = JWTBearer()
