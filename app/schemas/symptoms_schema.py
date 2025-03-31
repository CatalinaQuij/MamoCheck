from pydantic import BaseModel
from typing import Dict, Optional
from bson import ObjectId

class SymptomsSchema(BaseModel):
    user_id: str
    secreciones: Optional[str] = None
    color_secrecion: Optional[str] = None
    quistes: bool = False
    irregularidades: bool = False
    granitos: bool = False
    dolor: bool = False
    hinchazon: bool = False
    erupciones: bool = False
    aumento_pechos: bool = False
    cambios_pezon: bool = False
    descripcion: Optional[str] = None

    class Config:
            json_encoders = {ObjectId: str}