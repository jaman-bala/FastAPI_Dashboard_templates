from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response
from starlette.responses  import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.config.connection import Base, engine, sess_db
from backend.user.crud.repositoryuser import UserRepository, SendEmailVerify
from backend.user.crud.security import verify_password, create_access_token, COOKIE_NAME, get_password_hash, \
    verify_token
from backend.user.model.models import UserModel

templates = Jinja2Templates(directory="templates")
router = APIRouter()

#db_engin
Base.metadata.create_all(bind=engine)


@router.get("/signin")
def login(req: Request):
    return templates.TemplateResponse("/login/signin.html", {"request": req})


@router.post("/signinuser")
def signin_user(response: Response, db: Session = Depends(sess_db), username: str = Form(), password: str = Form()):
    userRepository = UserRepository(db)
    db_user = userRepository.get_user_by_username(username)
    if not db_user:
        return RedirectResponse(url="/user/error404", status_code=302)

    if verify_password(password, db_user.password):
        token = create_access_token(db_user)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            expires=1800
        )
    return RedirectResponse(url="/", status_code=302)


@router.get("/signup")
def signup(req: Request):
    return templates.TemplateResponse("login/signup.html", {"request": req})


@router.post("/signupuser")
def signup_user(db: Session = Depends(sess_db), username: str = Form(), email: str = Form(), password: str = Form()):
    userRepository = UserRepository(db)
    db_user = userRepository.get_user_by_username(username)
    if db_user:
        return "username is not valid"

    signup = UserModel(email=email, username=username, password=get_password_hash(password))
    success = userRepository.create_user(signup)
    token = create_access_token(signup)
    SendEmailVerify.sendVerify(token)
    if success:
        return "create  user successfully"
    else:
        raise HTTPException(
            status_code=401, detail="Credentials not correct"
        )


@router.get('/verify/{token}')
def verify_user(token, db: Session = Depends(sess_db)):
    userRepository = UserRepository(db)
    payload = verify_token(token)
    username = payload.get("username")
    db_user = userRepository.get_user_by_username(username)

    if not username:
        raise HTTPException(
            status_code=401, detail="Credentials not correct"
        )
    if db_user.is_active == True:
        return "your account  has been allreay activeed"

    db_user.is_active = True
    db.commit()
    response = RedirectResponse(url="/user/signin")
    return response
    # http://127.0.0.1:8000/user/verify/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNseWRleTAxMzEiLCJlbWFpbCI6ImNseWRleUBnbWFpbC5jb20iLCJyb2xlIjoidXNlciIsImFjdGl2ZSI6ZmFsc2V9.BKektCLzr47qn-fRtnGVulSdYlcMdemJQO_p32jWDk0


@router.get("/error404")
def error(req: Request):
    return templates.TemplateResponse("/error/404.html", {"request": req})