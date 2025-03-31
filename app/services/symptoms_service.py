import os
import requests
from fastapi import APIRouter, HTTPException
from app.models.symptoms_model import ReportData

GEMINI_API_KEY = "AIzaSyDQWd56NBG0B79C7La-4GdV3H2ElPBDaOc"

# Verificar que la API Key se haya cargado correctamente
if not GEMINI_API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

# Definir la URL de la API de Gemini
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Crear router
router = APIRouter()

@router.post("/generate_suggestion/")
async def generate_suggestion(report: ReportData):
    try:
        # Construir el prompt
        prompt = f"""
        Un usuario con ID {report.user_id} ha reportado los siguientes síntomas en su autoexamen mamario:
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

        Basado en estos síntomas, ¿puedes generar una recomendación médica para este usuario?
        """

        # Formato del payload para la API de Gemini
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        headers = {"Content-Type": "application/json"}

        # Llamada a la API de Gemini
        response = requests.post(GEMINI_URL, json=payload, headers=headers)
        response_data = response.json()

        # Extraer la respuesta generada
        if "candidates" in response_data:
            suggestion = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            suggestion = "No se pudo generar una sugerencia en este momento."

        return {"suggestion": suggestion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando la sugerencia: {str(e)}")