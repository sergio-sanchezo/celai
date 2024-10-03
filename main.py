# LOAD ENV VARIABLES
import os
from dotenv import load_dotenv
from loguru import logger as log

# Cargar el archivo .env correcto según el entorno
env = os.getenv('ENV', 'development')  # Por defecto, usa 'development'

if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

# Importar módulos de Cel.ai
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.message_gateway import MessageGateway
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.assistants.function_response import RequestMode
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.connectors.vapi.vapi_connector import VAPIConnector
from cel.middlewares import SessionMiddleware, RedisBlackListVapiMiddleware
from cel.gateway.request_context import RequestContext

# Importar el servicio de Salesforce
from services.salesforce import SalesforceService

from cel.assistants.common import Param
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.assistants.function_context import FunctionContext
import json



if __name__ == "__main__":

    # Instancia del servicio de Salesforce con parámetros del entorno
    sf_service = SalesforceService(
        username=os.getenv("SF_USERNAME"),
        password=os.getenv("SF_PASSWORD"),
        security_token=os.getenv("SF_SECURITY_TOKEN"),
        consumer_key=os.getenv("SF_CONSUMER_KEY"),
        consumer_secret=os.getenv("SF_CONSUMER_SECRET"),
        domain="test" if env == "development" else "login"  # Cambia a "login" en producción si es necesario
    )

    # Registrar middlewares
    auth = SessionMiddleware()
    blacklist = RedisBlackListVapiMiddleware(redis="redis://localhost:6379/0")

    # Configurar el prompt desde el archivo prompt.txt
    prompt = open("prompt.txt", "r", encoding="utf-8").read()
    prompt_template = PromptTemplate(prompt)

    async def get_customer_info(lead: ConversationLead):
        customer_phone = lead.to_dict().get("call_object", {}).get("customer", {}).get("number", "+56352280778")
        result = sf_service.get_user_by_phone(customer_phone)
        # transformar a string
        result = json.dumps(result)
        return result if result else "Pendiente de información"

    agent_settings = MacawSettings(
        core_model='gpt-4o-mini',
    )

    ast = MacawAssistant(
        prompt=prompt_template, 
        state={
        "customer_data": get_customer_info
        },
        settings=agent_settings
    )

    mdm = MarkdownRAG("demo", file_path="qa.md", split_table_rows=True, encoding="utf-8")

    # Cargar desde el archivo markdown, luego dividir el contenido y almacenarlo.
    mdm.load()

    # Registrar el modelo RAG con el asistente
    ast.set_rag_retrieval(mdm)

    @ast.function("buscarPorRut", "El cliente proporciona su RUT para buscar su información", [
        Param(name="RUT", type="string", description="El RUT del cliente por ej 12345678", required=True)
    ])
    async def handle_buscar_por_rut(session, params, ctx: FunctionContext):
        log.critical(f"Got buscarPorRut call with params: {params}")
        rut = params.get("RUT", False)
        if not rut:
            return FunctionContext.response_text("No se proporcionó un RUT", request_mode=RequestMode.SINGLE)
        else:
            attempts = 0
            max_attempts = 3
            result = None
            error_occurred = False
            
            while attempts < max_attempts:
                try:
                    result = sf_service.get_user_by_rut(rut)
                    if result:
                        await ctx.state.set_key_value(session, "customer_data", json.dumps(result))
                        return FunctionContext.response_text(f"La información del cliente es: {json.dumps(result)}", request_mode=RequestMode.SINGLE)
                    else:
                        # No result found but no error occurred
                        break
                except Exception as e:
                    log.error(f"Attempt {attempts + 1} failed with error: {str(e)}")
                    attempts += 1
                    error_occurred = True
            
            if error_occurred:
                return FunctionContext.response_text(
                    "Lamentablemente hemos tenido un inconveniente técnico intentando identificar la cuenta por RUT, "
                    "por lo que lamentablemente no lo puedo asistir con la consulta. "
                    "¿Desea que te derive con un asesor comercial o técnico?",
                    request_mode=RequestMode.SINGLE
                )
            else:
                return FunctionContext.response_text(
                    "No se encontró información para el RUT proporcionado. "
                    "¿Desea que te derive con un asesor comercial o técnico?",
                    request_mode=RequestMode.SINGLE
                )

    @ast.function("crearProspecto", "El cliente proporciona su información para crear un prospecto", [
        Param(name="first_name", type="string", description="Nombre del cliente", required=True),
        Param(name="last_name", type="string", description="Apellido del cliente", required=True),
        Param(name="company", type="string", description="Empresa del cliente", required=True),
        Param(name="rut", type="string", description="RUT del cliente", required=True),
        Param(name="phone", type="string", description="Teléfono del cliente", required=True),
        Param(name="email", type="string", description="Email del cliente, debe ser un formato válido", required=True),
        Param(name="comment", type="string", description="Resumen del producto o servicio sobre el cual se está interesado", required=True)
    ])
    async def handle_crear_prospecto(session, params, ctx: FunctionContext):
        log.critical(f"Got crearProspecto call with params: {params}")

        attempts = 0
        max_attempts = 3
        result = None
        error_occurred = False

        while attempts < max_attempts:
            try:
                result = sf_service.create_prospect(params)
                if result:
                    return FunctionContext.response_text(f"Prospecto creado con éxito", request_mode=RequestMode.SINGLE)
                else:
                    # Si el resultado es vacío, significa que la creación del prospecto falló, no tiene sentido reintentar.
                    break
            except Exception as e:
                log.error(f"Attempt {attempts + 1} to create prospect failed with error: {str(e)}")
                attempts += 1
                error_occurred = True

        if error_occurred:
            return FunctionContext.response_text(
                "Lamentablemente hemos tenido un inconveniente técnico al intentar crear el prospecto. "
                "Por lo tanto, no puedo completar la solicitud en este momento. "
                "¿Desea que te derive con un asesor comercial o técnico?",
                request_mode=RequestMode.SINGLE
            )
        else:
            return FunctionContext.response_text(
                "No se pudo crear el prospecto con la información proporcionada. "
                "¿Desea que te derive con un asesor comercial o técnico?",
                request_mode=RequestMode.SINGLE
            )

    gateway = MessageGateway(
        webhook_url=os.environ.get("WEBHOOK_URL"),
        assistant=ast,
        host="127.0.0.1", port=int(os.environ.get("PORT", 3000)),
        # VAPI uses streaming mode, no need for adaptive mode
    )

    # VoIP Connector
    conn = VAPIConnector(
        salesforce_service=sf_service,
    )

    # Registrar los middlewares con el gateway
    gateway.register_middleware(blacklist)

    # Registrar el conector con el gateway
    gateway.register_connector(conn)

    # Iniciar el gateway y comenzar a procesar mensajes
    gateway.run()
