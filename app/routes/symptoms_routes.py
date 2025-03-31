from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from app.schemas.symptoms_schema import SymptomsSchema
from app.db.database import database
from bson import ObjectId
from datetime import datetime
from app.models.symptoms_model import ReportData
from app.services.symptoms_service import generate_suggestion

router = APIRouter()
reports_collection = database.get_collection("reports")
users_collection = database.get_collection("users")
templates = Jinja2Templates(directory="templates")

#  Crear Reporte (POST)
@router.post("/reports/", status_code=201)
async def create_report(report: SymptomsSchema):
    """Crea un reporte con fecha de creación y lo asocia a un usuario existente"""
    
    if not ObjectId.is_valid(report.user_id):
        raise HTTPException(status_code=400, detail="ID de usuario no válido")

    user = users_collection.find_one({"_id": ObjectId(report.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    report_dict = report.dict()
    report_dict["user_id"] = ObjectId(report_dict["user_id"])
    report_dict["created_at"] = datetime.utcnow()
    report_dict["ai_messages"] = []

    inserted = reports_collection.insert_one(report_dict)

    users_collection.update_one(
        {"_id": ObjectId(report.user_id)},
        {"$push": {"reports": inserted.inserted_id}}
    )

    return {"message": "Reporte guardado correctamente", "id": str(inserted.inserted_id)}

#  Obtener Reporte por ID (GET)
@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    report["_id"] = str(report["_id"])
    report["user_id"] = str(report["user_id"])
    return report

#  Obtener Reportes por ID de Usuario (GET)
@router.get("/reports/user/{user_id}")
async def get_reports_by_user_id(user_id: str):
    """Devuelve todos los reportes de un usuario, incluyendo fecha de creación, síntomas y mensajes de la IA"""

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario no válido")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    reports = list(reports_collection.find({"user_id": ObjectId(user_id)}))

    for report in reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
        report["created_at"] = report.get("created_at", "Fecha no disponible")  
        report["symptoms"] = report.get("symptoms", [])
        report["ai_messages"] = report.get("ai_messages", [])

    return {"user_id": user_id, "reports": reports}

#  Obtener Todos los Reportes (GET)
@router.get("/reports/")
async def get_all_reports():
    reports = list(reports_collection.find({}))
    for report in reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
    return reports

#  Actualizar Reporte (PUT)
@router.put("/reports/{report_id}")
async def update_report(report_id: str, report: SymptomsSchema):
    """Actualiza un reporte existente"""
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID de reporte no válido")

    updated = database.get_collection("reports").update_one(
        {"_id": ObjectId(report_id)},
        {"$set": report.dict()}
    )

    if updated.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    return {"message": "Reporte actualizado correctamente"}

#  Eliminar Reporte (DELETE)
@router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    deleted = reports_collection.delete_one({"_id": ObjectId(report_id)})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # También eliminamos el reporte de la lista en el usuario
    users_collection.update_one(
        {"reports": ObjectId(report_id)},
        {"$pull": {"reports": ObjectId(report_id)}}
    )

    return {"message": "Reporte eliminado correctamente"}

@router.get("/reports/edit/{report_id}")
async def edit_report_page(request: Request, report_id: str):
    """Renderiza la página de edición del reporte"""
    
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID de reporte no válido")

    report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    report["_id"] = str(report["_id"])  # Convertir ObjectId a string

    return templates.TemplateResponse("edit_report.html", {"request": request, "report": report})

@router.post("/generate_suggestion/")
async def generate_suggestion_route(report: ReportData):
    return await generate_suggestion(report)
