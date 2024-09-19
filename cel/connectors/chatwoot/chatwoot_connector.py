import os
import json
import time
import httpx
import aiohttp
from typing import Any, Callable, Dict, List
from fastapi import APIRouter, BackgroundTasks, Request
from loguru import logger as log
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import (
    OutgoingMessage,
    OutgoingMessageType,
    OutgoingLinkMessage,
    OutgoingSelectMessage,
    OutgoingTextMessage,
)
from cel.connectors.chatwoot.constants import BASE_URL, AUTH_CHATWOOT
from cel.connectors.chatwoot.utils import build_headers
from .model.chatwoot_lead import ChatwootLead
from .model.chatwoot_message import ChatwootMessage

from .functions.utils import changed_field, is_message, is_reaction

def nothing(*args):
    pass

class ChatwootConnector(BaseConnector):

    def __init__(
        self,
        token: str = None,
        verify_token: str = None,
        endpoint_prefix: str = None,
        web_url: str = None,
        stream_mode: StreamMode = StreamMode.FULL,
    ):
        """
        Inicializar el conector de chatwoot cloud Api con el token de acceso que se provee para cada cuenta

        Args:
            token[str]: Token de acceso de la cuenta de chatwoot
            endpoint_prefix[str]: Endpoint de consulta para chatwoot
            webhook_prefix[str]: el prefijo del webhook, por defecto retorna "/chatwoot"
        """
        # Nos aseguramos de que el token no este vacio
        # assert token is not None, "Token not provided"

        log.debug("Creating Chatwoot connector")
        # Definir las rutas para las cuales se hacen las consultas o comunicaciones
        self.prefix = "/chatwoot"
        self.another_prefix = "/messages"
        self.endpoint_prefix = endpoint_prefix
        self.url = f"{BASE_URL}"
        self.token = AUTH_CHATWOOT
        self.paused = False
        self.verify_token = verify_token # puede no ser necesario dependiendo de como deseemos hacerlo
        self.stream_mode = stream_mode
        self.verification_handler = nothing
        self.router = APIRouter(prefix=self.prefix)

        self.__build_routes(endpoint_prefix, self.router)

    def __build_routes(self, endpoint_prefix: str, router: APIRouter):
        print("Construyendo las rutas necesarias")
        assert endpoint_prefix is not None, "Endpoint is not provided"
        
        """
        Definimos las rutas a trabajar para mensajes de texto tanto para abstraerlos como para crearlos
        https://app.chatwoot.com/platform/api/v1/accounts/{account_id}/account_users
        """
        # post para mensajes
        @router.post(f"{self.another_prefix}")
        async def send_message_chatwoot(r: Request, background_tasks: BackgroundTasks):
            try:
                # Handle Webhook Subscriptions
                data = await r.json()
                background_tasks.add_task(self.__process_message, data)
                return {"success": True}
            except Exception as e:
                # Avoid replaying the message
                return {"success": False}
        

    # async def __process_message(self, data: dict):      
    #     changed_field = self.changed_field(data)
    #     log.debug(f"Changed field: {changed_field}")
    #     if changed_field == "messages":
    #         if self.is_reaction(data):
    #             log.debug("Reaction received")
    #             return
    #         new_message = self.is_message(data)
    #         log.debug(f"New message: {new_message}")
    #         if new_message:
    #             msg = await ChatwootMessage.load_from_message(data=data, 
    #                                                     token=self.token,
    #                                                     connector=self)
    #             await self.__mark_as_read(msg.id)
    #             if self.gateway:
    #                 async for m in self.gateway.process_message(msg, mode=self.stream_mode):
    #                     pass

    async def __process_message(self, data: Dict[str, Any]):
        try:
            log.debug("Receive an message for chatwoot")
            msg = await ChatwootMessage.load_from_message(data, connector=self)
            print(msg, '__process_message')
            if self.paused:
                log.warning("Connector is paused, ignoring message")
                return {"status": "paused"}
            
            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass
            else:
                log.critical("Gateway not set in Connector")
                raise Exception("Gateway not set in Connector")
            
            
        except Exception as e:
            log.error(f"Error processing message: {e}")
            return Exception("Gateway not set in Chatwoot Connector")
    
    def name(self) -> str:
        return "chatwoot"
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway

    async def send_typing_action(self, lead: ChatwootLead):
        log.warning("Sending typing action to Web is not implemented yet")


    async def send_text_message(self, 
                                lead: ChatwootLead, 
                                text: str, 
                                metadata: dict = {}, 
                                is_partial: bool = True):
        """ Send a text message to the lead. The simplest way to send a message to the lead.
        
        Args:
            - lead[WhatsappLead]: The lead to send the message
            - text[str]: The text to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """
        
        assert isinstance(lead, ChatwootLead), "lead must be instance of WhatsappLead"
        log.debug("Estas enviando un mensaje: ", text)

        data = {
            "content": text
        }
        account = 5
        conversation = 321
        url = f"{self.url}/accounts/{account}/conversations/{conversation}/messages"

        headers = build_headers(self.token)
        log.info(f"Sending message for chatwoot part 1")

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.info(f"Message sent to for chatwoot part 2")
                else:
                    log.error(await r.json())


    
    # Funcion que retorna el mensaje del bot
    async def send_select_message(
        self,
        lead: ChatwootLead,
        text: str,
        options: List[str],
        metadata: dict = {},
        is_partial: bool = True,
    ):
        print(f"Bot: {text}")

    async def send_link_message(
        self,
        lead: ChatwootLead,
        text: str,
        links: List[Dict[str, str]],
        metadata: dict = {},
        is_partial: bool = True,
    ):
        print(f"Bot: {text}")

    async def _send_link(self, 
                         link_label: str, 
                         body: str | None,
                         link: str,
                         recipient_id: str,
                         footer: str | None = None,
                         image_url: str = None) -> None:
        await self._send_cta_url(
            recipient_id=recipient_id,
            cta_url={
                "type": "cta_url",
                "header": {
                    "type": "image",
                    "image": {"link": image_url}
                } if image_url else None,
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": link_label,
                        "url": link
                    }
                }                
            }
        )

    async def send_message(self, message: OutgoingMessage):
        assert isinstance(
            message, OutgoingMessage
        ), "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, ChatwootLead), "lead must be an instance of WebLead"
        lead = message.lead

        if message.type == OutgoingMessageType.TEXT:
            assert isinstance(
                message, OutgoingTextMessage
            ), "message must be an instance of OutgoingTextMessage"
            await self.send_text_message(
                lead,
                message.content,
                metadata=message.metadata,
                is_partial=message.is_partial,
            )

        if message.type == OutgoingMessageType.SELECT:
            assert isinstance(
                message, OutgoingSelectMessage
            ), "message must be an instance of OutgoingSelectMessage"
            await self.send_select_message(
                lead,
                message.content,
                options=message.options,
                metadata=message.metadata,
                is_partial=message.is_partial,
            )

        if message.type == OutgoingMessageType.LINK:
            assert isinstance(
                message, OutgoingLinkMessage
            ), "message must be an instance of OutgoingLinkMessage"
            await self.send_link_message(
                lead,
                message.content,
                links=message.links,
                metadata=message.metadata,
                is_partial=message.is_partial,
            )

        return message
    
    async def _send_cta_url(
        self, cta_url: Dict[Any, Any], 
        recipient_id: str
    ) -> Dict[Any, Any]:
        """
        Sends a call to action url message to a WhatsApp user

        Args:
            cta_url[dict]: A dictionary containing the cta url data
            recipient_id[str]: Phone number of the user with country code wihout +

        check
        
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "interactive",
            "interactive": cta_url,
        }
        headers = build_headers(self.token)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.debug(f"Message sent to {recipient_id}")
                else:
                    log.error(await r.json())

    def get_router(self) -> APIRouter:
        return self.router

    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway

        assert isinstance(
            gateway, MessageGateway
        ), "gateway must be an instance of MessageGateway"
        self.gateway = gateway

    def startup(self, context: MessageGatewayContext):
        assert context.webhook_url, "webhook_url must be set in the context"
        assert context.webhook_url.startswith(
            "https"
        ), f"webhook_url must be HTTPS, got: {context.webhook_url}.\
            Be sure that your url is public and has a valid SSL certificate."

        webhook_url = f"{context.webhook_url}{self.prefix}{self.endpoint_prefix}"
        log.debug(f"Starting Web connector with url: {webhook_url}")

    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down Web Connector")

    def pause(self):
        log.debug("Pausing Web Connector")
        self.paused = True

    def resume(self):
        log.debug("Resuming Web Connector")
        self.paused = False

    # all the files starting with _ are imported here, and should not be imported directly.
    changed_field = staticmethod(changed_field)
    is_message = staticmethod(is_message)
    is_reaction = staticmethod(is_reaction)