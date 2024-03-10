from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response
from starlette.responses  import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.config.connection import Base, engine, sess_db
from backend.user.crud.repositoryuser import UserRepository
from backend.user.crud.security import verify_password, create_access_token, COOKIE_NAME, is_admin
from backend.user.model.models import UserModel
from backend.user.model.schemas import Roles

templates = Jinja2Templates(directory="templates")
router = APIRouter()

Base.metadata.create_all(bind=engine)


@router.get("/signin")
def admin(request: Request):
    return templates.TemplateResponse("/dashboard/login.html", {"request": request})


@router.post("/signinadmin")
def signin_admin(response: Response, db: Session = Depends(sess_db), username: str = Form(), password: str = Form()):
    adminRepository = UserRepository(db)
    db_admin = adminRepository.get_user_by_username(username)

    if not db_admin or db_admin.role != Roles.admin or not verify_password(password, db_admin.password):
        return RedirectResponse(url="/user/error404", status_code=302)

    token = create_access_token(db_admin)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        expires=1800
    )

    return RedirectResponse(url="/dashboard/index", status_code=302)


@router.get("/index")
def dashboard(request: Request):
    return templates.TemplateResponse("/dashboard/dashboard.html", {"request": request})
