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
@router.post("/reports/{user_id}", status_code=201)
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

    inserted = reports_collection.insert_one(report_dict)

    users_collection.update_one(
        {"_id": ObjectId(report.user_id)},
        {"$push": {"reports": inserted.inserted_id}}
    )

    return {"message": "Reporte guardado correctamente", "id": str(inserted.inserted_id)}

#  Obtener Reporte por ID (GET)
@router.get("/reportes/{report_id}")
async def get_report(report_id: str):
    if not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID no válido")

    report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    report["_id"] = str(report["_id"])
    report["user_id"] = str(report["user_id"])
    return report

#  Obtener Todos los Reportes (GET)
@router.get("/reports/")
async def get_all_reports():
    reports = list(reports_collection.find({}))
    for report in reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
    return reports

#  Actualizar Reporte (PUT)
@router.put("/reports/{user_id}/{report_id}")
async def update_report(user_id: str, report_id: str, report: SymptomsSchema):
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(report_id):
        raise HTTPException(status_code=400, detail="ID de usuario o de reporte no válido")

    existing_report = reports_collection.find_one({
        "_id": ObjectId(report_id),
        "user_id": ObjectId(user_id)
    })

    if not existing_report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado o no pertenece al usuario")

    updated_data = report.dict()
    updated_data["user_id"] = ObjectId(user_id)

    updated = reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": updated_data}
    )

    if updated.modified_count == 0:
        return {"message": "No hubo cambios en el reporte"}

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

@router.get("/reports/edit/{user_id}/{report_id}")
async def edit_report_page(request: Request, user_id: str, report_id: str):
    """Renderiza la página de edición del reporte"""

    if not ObjectId.is_valid(report_id) or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario o reporte no válido")

    report = reports_collection.find_one({
        "_id": ObjectId(report_id),
        "user_id": ObjectId(user_id)
    })
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado o no pertenece al usuario")

    report["_id"] = str(report["_id"])
    report["user_id"] = str(report["user_id"])

    # Obtener el usuario para mostrar su nombre
    username = "Usuario"
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        username = user.get("username", "Usuario")

    return templates.TemplateResponse(
        "edit_report.html",
        {"request": request, "report": report, "username": username}
    )

