from pydantic import BaseModel

class Concepto(BaseModel):
    concepto: str
    definicion: str
    ejemplo: str

numero_primo = Concepto(
    concepto="Número primo",
    definicion="Número entero mayor que 1 con dos divisores.",
    ejemplo="7 es un número primo."
)

print(numero_primo)
print(numero_primo.concepto)
print(numero_primo.definicion)
print(numero_primo.ejemplo)