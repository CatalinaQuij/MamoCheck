from fastapi import APIRouter, HTTPException, Request, Form, Depends
from app.schemas.user_schema import UserSchema
from app.db.database import database
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

router = APIRouter()
users_collection = database.get_collection("users")
reports_collection = database.get_collection("reports")
templates = Jinja2Templates(directory="templates")

#  Crear Usuario (POST)
@router.post("/users/register/")
async def register_user(user: UserSchema):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")

    user_data = user.dict()
    user_data["password"] = generate_password_hash(user_data["password"])
    user_data["reports"] = []  # Lista vacía para almacenar reportes

    inserted = users_collection.insert_one(user_data)
    return {"message": "Usuario registrado exitosamente", "id": str(inserted.inserted_id)}

#  Obtener Usuario por ID (GET) con Reportes (Solo ID y Fecha)
@router.get("/users/{user_id}")
async def get_user_with_reports(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Obtener los reportes del usuario y solo devolver ID y fecha
    report_ids = user.get("reports", [])
    reports = list(reports_collection.find({"_id": {"$in": report_ids}}, {"_id": 1, "created_at": 1}))

    formatted_reports = [{"id": str(report["_id"]), "created_at": report.get("created_at", "Sin fecha")} for report in reports]

    user["_id"] = str(user["_id"])
    user["reports"] = formatted_reports

    return user

#  Obtener Todos los Usuarios (GET)
@router.get("/users/")
async def get_all_users():
    users = list(users_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"])
        user["reports"] = [str(report_id) for report_id in user.get("reports", [])]
    return users

#  Actualizar Usuario (PUT)
@router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserSchema):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    user_data = user.dict()
    user_data["password"] = generate_password_hash(user_data["password"])

    updated = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_data}
    )

    if updated.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": "Usuario actualizado correctamente"}

#  Eliminar Usuario (DELETE)
@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    deleted = users_collection.delete_one({"_id": ObjectId(user_id)})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # También eliminamos todos sus reportes
    reports_collection.delete_many({"user_id": ObjectId(user_id)})

    return {"message": "Usuario eliminado correctamente, junto con sus reportes"}

# Ruta GET para mostrar la página de login
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Ruta POST para procesar el login
@router.post("/login")
async def login_user(
    username: str = Form(...),
    password: str = Form(...)
):
    user = users_collection.find_one({"username": username})

    if not user or not check_password_hash(user["password"], password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    return JSONResponse(
        status_code=200,
        content={"message": "Inicio de sesión exitoso", "redirect": f"/reports/{user['_id']}"}
    )

@router.get("/reports/{user_id}")
async def user_reports_page(request: Request, user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario no válido")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    report_ids = user.get("reports", [])
    reports = list(reports_collection.find({"_id": {"$in": report_ids}}, {"_id": 1, "created_at": 1}))

    formatted_reports = [{"id": str(report["_id"]), "created_at": report.get("created_at", "Sin fecha")} for report in reports]

    return templates.TemplateResponse(
        "reports.html", 
        {"request": request, "user_id": user_id, "reports": formatted_reports}
    )