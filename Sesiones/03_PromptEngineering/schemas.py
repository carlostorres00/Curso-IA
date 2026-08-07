from pydantic import BaseModel

class Concepto(BaseModel):
    concepto: str
    definicion: str
    ejemplo: str