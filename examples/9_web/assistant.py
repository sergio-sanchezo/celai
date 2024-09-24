# LOAD ENV VARIABLES
import os
import sys

# from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv

# Cargar el archivo .env correcto según el entorno
env = os.getenv('ENV', 'development')  # Por defecto, usa 'development'

if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

# REMOVE THIS BLOCK IF YOU ARE USING THIS SCRIPT AS A TEMPLATE
# -------------------------------------------------------------
import sys
from pathlib import Path

# Add parent directory to path
path = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(path.parents[1]))
# -------------------------------------------------------------


# Import Cel.ai modules
from cel.gateway.message_gateway import MessageGateway
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.connectors.web.web_connector import WebConnector
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.assistants.common import Param
from cel.assistants.function_context import FunctionContext
from cel.gateway.message_gateway import StreamMode

import os
from loguru import logger as log
log.remove()
log.add(sys.stdout, format="<level>{level: <8}</level> | "
    "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# Setup prompt
# Read from the file prompt.txt
prompt = """
[Identity]
Eres Netia, un asistente responsable de proveer información sobre productos y servicios que los ayude empleados de la empresa Netline.

[Style]
- Sé formal, claro y conciso.
- Mantén un tono respetuoso y profesional.
- Alinea los mensajes con la misión de Netline de ofrecer soluciones simples y efectivas.

[Response Guideline]
- Utiliza saludos y cierres formales.
- Si es apropiado, destaca el soporte 24/7 y los servicios de instalación rápida que ofrece Netline.
- Redacción de correos
- Para correos electronicos resume el propósito del correo en las primeras dos oraciones.
- Redacción de descripciones de productos y servicios
- Q&A de productos y servicios que ofrece la compañia
- Ayudar a armar ideas o generar propuestas comerciales
- Asegúrate de que los asuntos de los correos electrónicos sean claros, descriptivos y relacionados directamente con los servicios de Netline (tal como del Proceso de instalación de NetAir y otros servicios).

"""

# Create the prompt template
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template,
    settings=MacawSettings(
        core_temperature=0, core_max_tokens=300, core_model="gpt-4o-mini"
    ),
)


# Configure the RAG model using the MarkdownRAG provider
# by default it uses the CachedOpenAIEmbedding for text2vec
# and ChromaStore for storing the vectors
mdm = MarkdownRAG("demo", file_path="examples/9_web/qa.md", encoding="utf-8")
# Load from the markdown file, then slice the content, and store it.
mdm.load()
# Register the RAG model with the assistant
ast.set_rag_retrieval(mdm)


# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="0.0.0.0",
    port=3000,
)

# VoIP Connector

conn = WebConnector(web_url="http://localhost:3001/messages", stream_mode=StreamMode.DIRECT)

# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run()