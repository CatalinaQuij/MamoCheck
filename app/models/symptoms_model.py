from pydantic import BaseModel

class ReportData(BaseModel):
    user_id: str
    secreciones: str
    color_secrecion: str
    descripcion: str
    quistes: bool
    irregularidades: bool
    granitos: bool
    dolor: bool
    hinchazon: bool
    erupciones: bool
    aumento_pechos: bool
    cambios_pezon: bool
