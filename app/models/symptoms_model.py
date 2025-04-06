from typing import Optional
from pydantic import BaseModel

class ReportData(BaseModel):
    user_id: str
    quistes: Optional[bool] = False
    irregularidades: Optional[bool] = False
    granitos: Optional[bool] = False
    dolor: Optional[bool] = False
    hinchazon: Optional[bool] = False
    secreciones: Optional[str] = None
    color_secrecion: Optional[str] = None
    erupciones: Optional[bool] = False
    aumento_pechos: Optional[bool] = False
    cambios_pezon: Optional[bool] = False
    descripcion: Optional[str] = ""
