from typing import List, Optional, Tuple
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()


class PropertyPreferences(BaseModel):
    ubicacion: str
    tipo_de_propiedad: str
    habitaciones: int
    banos: int
    caracteristicas_adicionales: Optional[List[str]]
    rango_de_precio: str


# Templates para los System Prompts
PREFERENCES_PROMPT_TEMPLATE = (
    "Eres un agente especializado en búsqueda de propiedades. "
    "Tu tarea principal es ayudar al cliente a identificar las características de la propiedad que busca. "
    "Sigue estas reglas: "
    "1. Haz preguntas claras y específicas para recopilar datos sobre: "
    "- Ubicación o ciudad deseada. "
    "- Tipo de propiedad (casa, departamento, terreno, etc.). "
    "- Cantidad de habitaciones. "
    "- Cantidad de baños. "
    "- Otras características deseadas (jardín, piscina, estacionamiento, etc.). "
    "- Rango de precio estimado. "
    "2. Confirma cada respuesta del cliente para asegurarte de que la información es correcta y ofrece la oportunidad de ajustar detalles si es necesario. "
    "3. Si el cliente no sabe qué responder a una pregunta, ofrécele ejemplos o categorías comunes para ayudarlo a decidir. "
    "4. Finaliza las preguntas cuando el cliente indique que no tiene más información que agregar o si confirmas que todos los datos necesarios han sido recopilados. "
    "5. Al finalizar, devuelve un mensaje y un indicador de finalización en el formato: "
    '{"message": "str", "finished": true/false}. '
    "En cada interacción, prioriza la claridad y guía al cliente hacia respuestas útiles. "
    "Si detectas información contradictoria o confusa, pregunta amablemente para clarificar. "
    "Mantén el enfoque en los intereses y necesidades del cliente."
)

JSON_RESPONSE_PROMPT_TEMPLATE = (
    "Eres un agente especializado en organizar información de propiedades. "
    "Tu tarea es recibir las preferencias recopiladas por otro agente en formato de texto y devolverlas como un JSON estructurado. "
    "Ejemplo: "
    '{"ubicacion":"Ciudad X","tipo_de_propiedad":"Casa","habitaciones":3,"banos":2,'
    '"caracteristicas_adicionales":["jardín","piscina"],"rango_de_precio":"100,000 - 150,000 USD"} '
    "Procesa la información y devuelve únicamente el JSON."
)
