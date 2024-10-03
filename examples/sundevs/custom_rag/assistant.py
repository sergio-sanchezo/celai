import os
from dotenv import load_dotenv
load_dotenv()

from cel.connectors.cli.cli_connector import CliConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.custom_rag import CustomRAGRetriever
from cel.model.common import ContextMessage
from cel.rag.stores.custom.custom_store import BackendStore
from cel.rag.providers.markdown_rag import MarkdownRAG

# Setup prompt
prompt = (
    "You are a Q&A Assistant called Celia."
    " You can help a user to send money."
    " Keep responses short and to the point."
)

prompt_template = PromptTemplate(prompt)

# Create the assistant
ast = MacawAssistant(prompt=prompt_template)

# Create the BackendStore
backend_store = BackendStore(
    base_url="http://localhost:3001",
    api_key=os.environ.get("BACKEND_API_KEY"),  # Replace with your API key
    account_id="6660e6f0b6dc5276d5f5d09f"       # Replace with your account ID
)


# Instantiate the retriever
retriever = CustomRAGRetriever(store=backend_store)

# Register the retriever with the assistant
ast.set_rag_retrieval(retriever)

# Create the Message Gateway
gateway = MessageGateway(ast)

# Use the Telegram connector
conn = CliConnector(
    stream_mode=StreamMode.FULL
)

gateway.register_connector(conn)

# Start the gateway
gateway.run()
