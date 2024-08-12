"""
Hello World AI Assistant Example
---------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to get started with Cel.ai for creating intelligent assistants.

Framework: Cel.ai
License: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

Usage:
------
Configure the required environment variables in a .env file in the root directory of the project.
The required environment variables are:
- WEBHOOK_URL: The webhook URL for the assistant, you can use ngrok to create a public URL for your local server.
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.

Then run this script to see a basic AI assistant in action.

Note:
-----
Please ensure you have the Cel.ai framework installed in your Python environment prior to running this script.
"""

import os
from loguru import logger as log

# Load .env variables
from dotenv import load_dotenv
load_dotenv(override=True)


# REMOVE THIS BLOCK IF YOU ARE USING THIS SCRIPT AS A TEMPLATE
# -------------------------------------------------------------
import sys
from pathlib import Path
# Add parent directory to path
path = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(path.parents[1]))
# -------------------------------------------------------------

# Import Cel.ai modules
from cel.connectors.cli.cli_connector import CliConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.common import Param
from cel.assistants.function_context import FunctionContext

# disable logs
log.remove()

# Setup prompt from prompt.txt, decode it in latin-1
prompt = open("prompt.txt", "r", encoding="latin-1").read()


prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template
)



@ast.function('obtenerClientePorId', 'Encuentra información del cliente usando el ID de la factura', params=[
    Param('idFactura', 'string', 'ID de la factura', required=True)
])
async def obtener_cliente_por_id(session, params, ctx: FunctionContext):
    log.debug(f"Got obtenerClientePorId from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Información del cliente encontrada.", request_mode=RequestMode.SINGLE)

@ast.function('construccionHorariosAtencion', 'Verifica los horarios de atencion de los diferentes equipos de asesores cuando el usuario solicita los horarios de atencion', params=[])
async def construccion_horarios_atencion(session, params, ctx: FunctionContext):
    log.debug(f"Got construccionHorariosAtencion from client:{ctx.lead.conversation_from.name}")
    return FunctionContext.response_text("Horarios de atención verificados.", request_mode=RequestMode.SINGLE)

@ast.function('verificarHorarioAtencion', 'Verifica si el asesor está dentro del horario de atención', params=[
    Param('equipo', 'string', 'Equipo al que se debe escalar el caso (administracion, ventas, soporte)', required=True, enum=["administracion", "ventas", "soporte"])
])
async def verificar_horario_atencion(session, params, ctx: FunctionContext):
    log.debug(f"Got verificarHorarioAtencion from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Horario de atención verificado.", request_mode=RequestMode.SINGLE)

@ast.function('escalarAsesor', 'Escala el caso a un asesor humano', params=[
    Param('titulo', 'string', 'Título del caso', required=True),
    Param('motivo', 'string', 'Motivo detallado por el que el cliente necesita hablar con un asesor humano', required=True),
    Param('equipo', 'string', 'Equipo al que se debe escalar el caso (administracion, ventas, soporte)', required=True, enum=["administracion", "ventas", "soporte"])
])
async def escalar_asesor(session, params, ctx: FunctionContext):
    log.debug(f"Got escalarAsesor from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Caso escalado a un asesor humano.", request_mode=RequestMode.SINGLE)

@ast.function('crearTicketSoporte', 'Crea un ticket de soporte para el cliente en Wispro', params=[
    Param('id_cliente', 'string', 'ID del cliente si está presente en el prompt'),
    Param('nombre', 'string', 'Nombre del cliente'),
    Param('apellido', 'string', 'Apellido del cliente'),
    Param('direccion', 'string', 'Dirección del cliente'),
    Param('titulo', 'string', 'Título del caso', required=True),
    Param('motivo', 'string', 'Motivo de la consulta', required=True),
    Param('equipo', 'string', 'Equipo al que se debe dirigir el caso (administracion, ventas, soporte)', required=True, enum=["administracion", "ventas", "soporte"])
])
async def crear_ticket_soporte(session, params, ctx: FunctionContext):
    log.debug(f"Got crearTicketSoporte from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Ticket de soporte creado.", request_mode=RequestMode.SINGLE)

@ast.function('encuestaSatisfaccion', 'Envía una encuesta de satisfacción al cliente para evaluar la atención recibida', params=[])
async def encuesta_satisfaccion(session, params, ctx: FunctionContext):
    log.debug(f"Got encuestaSatisfaccion from client:{ctx.lead.conversation_from.name}")
    return FunctionContext.response_text("Encuesta de satisfacción enviada.", request_mode=RequestMode.SINGLE)

@ast.function('seleccionarMedioUsado', 'Seleccionar el medio de pago que el usuario ha utilizado por el que quiere informar un pago', params=[
    Param('medioPago', 'string', 'Medio de pago utilizado por el cliente', required=True, enum=["homebanking", "app_alerta"])
])
async def seleccionar_medio_usado(session, params, ctx: FunctionContext):
    log.debug(f"Got seleccionarMedioUsado from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Medio de pago seleccionado.", request_mode=RequestMode.SINGLE)

@ast.function('estadoCasosDeSoporte', 'Obtener el numero del caso de soporte', params=[
    Param('idpublico', 'string', 'numero del caso de soporte', required=True)
])
async def estado_casos_de_soporte(session, params, ctx: FunctionContext):
    log.debug(f"Got estadoCasosDeSoporte from client:{ctx.lead.conversation_from.name} command with params: {params}")
    return FunctionContext.response_text("Número del caso de soporte obtenido.", request_mode=RequestMode.SINGLE)



# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(ast)

# For this example, we will use the Telegram connector
conn = CliConnector(
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run() 

