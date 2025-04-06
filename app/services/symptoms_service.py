import os
import requests
from fastapi import APIRouter, HTTPException
from app.models.symptoms_model import ReportData
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
GEMINI_API_KEY = "AIzaSyDQWd56NBG0B79C7La-4GdV3H2ElPBDaOc"

# Verificación básica
if not all([MONGO_URI, MONGO_DB_NAME, GEMINI_API_KEY]):
    raise ValueError("Faltan variables de entorno necesarias.")

# URL API Gemini
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db["users"]
reports_collection = db["reports"]

# FastAPI Router
router = APIRouter()

@router.post("/generate_suggestion/")
async def generate_suggestion(report: ReportData):
    try:
        # Buscar datos de la usuaria
        user_data = users_collection.find_one({"_id": ObjectId(report.user_id)})
        if not user_data:
            raise HTTPException(status_code=404, detail="❌ No se encontró información de la usuaria.")

        nombre = user_data.get("username", "Desconocido")
        edad = user_data.get("age", "no especificada")
        embarazo = "sí" if user_data.get("had_pregnancy") else "no"

        # Construcción del prompt
        prompt = f"""
        Datos de la usuaria:
        - Nombre: {nombre}
        - Edad: {edad}
        - Ha tenido embarazos: {embarazo}

        Reporte de autoexamen mamario:
        - Secreciones: {report.secreciones}
        - Color de Secreciones: {report.color_secrecion}
        - Descripción adicional: {report.descripcion}
        - Otros síntomas:
            - Quistes: {report.quistes}
            - Irregularidades: {report.irregularidades}
            - Granitos: {report.granitos}
            - Dolor: {report.dolor}
            - Hinchazón: {report.hinchazon}
            - Erupciones: {report.erupciones}
            - Aumento de tamaño de pechos: {report.aumento_pechos}
            - Cambios en la dirección del pezón: {report.cambios_pezon}

        Basado en estos datos personales y síntomas, ¿puedes generar una recomendación médica para esta usuaria? En la respuesta incluye la edad
        y nombre de la usuaria, es como si le estubieras hablando a ella, no debes alarmarla innecesariamente pero si debes mantener un tono
        amigable, serio y profesional. No olvides incluir una recomendación de acudir a un médico si es necesario y que esto no sustituye una consulta médica.
        Debes tutear a la usuaria. Recuerda considerar factores como la edad y el embarazo, por ejemplo, si la usuaria tiene 20 años y está embarazada, no es necesario alarmarla 
        por un quiste, pero si tiene 50 años y no está embarazada, sí es necesario. En general contempla otro tipo de factores subyacentes. 
        Categoriza la recomendación como títlo Resultado: Alarmante, Preocupante, Neutro o Positivo.
        """

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_URL, json=payload, headers=headers)
        response_data = response.json()

        suggestion = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No se pudo generar una sugerencia.").strip()

        # Guardar la sugerencia en la colección de reportes
        reports_collection.update_one(
            {"user_id": ObjectId(report.user_id), "descripcion": report.descripcion},
            {"$set": {"ai_suggestion": suggestion}}
        )

        return {"suggestion": suggestion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando la sugerencia: {str(e)}")
