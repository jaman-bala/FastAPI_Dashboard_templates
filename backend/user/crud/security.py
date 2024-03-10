from passlib.context import CryptContext  # pip install passlib
from fastapi.security import OAuth2PasswordBearer
from jose import jwt  # https://pypi.org/project/python-jose/ = pip install python-jose
from fastapi import Depends, Request, HTTPException, status

from backend.user.model.models import UserModel

JWT_SECRET = "NHBJKD;lashiofhah;uijhbujisdbui432df235h9p823;hr"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # pip install bcrypt
# save token to oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/signin")
COOKIE_NAME = "Authorization"


# create Token
def create_access_token(user):
    try:
        payload = {
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "active": user.is_active,

        }
        return jwt.encode(payload, key=JWT_SECRET, algorithm=ALGORITHM)
    except Exception as ex:
        print(str(ex))
        raise ex


# create verify Token
def verify_token(token):
    try:
        payload = jwt.decode(token, key=JWT_SECRET)
        return payload
    except Exception as ex:
        print(str(ex))
        raise ex


# password hash
def get_password_hash(password):
    return pwd_context.hash(password)


# password verify
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return user


def get_current_user_from_cookie(request: Request) -> UserModel:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        user = verify_token(token)
        return user


def is_admin(user: UserModel = Depends(get_current_user_from_token)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа к этому ресурсу",
        )
    return user