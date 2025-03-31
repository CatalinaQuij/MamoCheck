from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes.user_routes import router as user_router
from app.routes.symptoms_routes import router as report_router  
from fastapi.responses import JSONResponse
from app.db.database import database
from app.models.symptoms_model import ReportData
from werkzeug.security import check_password_hash
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from app.services import symptoms_service  

app = FastAPI()

app.include_router(user_router)
app.include_router(report_router)
users_collection = database.get_collection("users")
reports_collection = database.get_collection("reports")

# Servir archivos estáticos (CSS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(symptoms_service.router, prefix="/symptoms", tags=["symptoms"])

# Configurar Jinja2 para renderizar HTML
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "home_url": "/"})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/reporte")
async def login_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
