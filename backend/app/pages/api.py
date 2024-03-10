from fastapi import Request, APIRouter
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/about")
def home(request: Request):
    return templates.TemplateResponse("pages/about.html", {"request": request})
