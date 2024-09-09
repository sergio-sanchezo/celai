import os
import json
import time
import httpx
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
from .model.web_lead import WebLead
from .model.web_message import WebMessage


class WebConnector(BaseConnector):

    def __init__(
        self,
        web_url: str = None,
        stream_mode: StreamMode = StreamMode.FULL,
    ):
        log.debug("Creating Web connector")
        self.web_url = web_url or os.environ.get("WEB_URL")
        log.debug(self.web_url)
        self.prefix = "/web"
        self.endpoint = "/message"
        self.router = APIRouter(prefix=self.prefix)
        self.paused = False
        self.stream_mode = stream_mode
        self._create_routes(self.router)

        assert self.web_url, "WEB_URL env var must be set"

    def _create_routes(self, router: APIRouter):
        @router.post(f"{self.endpoint}")
        async def chat_completion(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            log.debug(data)
            background_tasks.add_task(self._process_message, data)
            print(data, "+" * 30)
            return {"status": "ok"}

        @router.post(f"{self.endpoint}/pruebas")
        async def text_persons(request: Request, background_tasks: BackgroundTasks):
            payload = await request.json()
            background_tasks.add_task(self._process_message, payload)
            return {"status": "ok"}

    async def _process_message(self, payload: Dict[str, Any]):
        try:
            log.debug("Received Web Message")
            msg = await WebMessage.load_from_message(payload, connector=self)

            if self.paused:
                log.warning("Connector is paused, ignoring message")
                return {"status": "paused"}

            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass
            else:
                log.critical("Gateway not set in Web Connector")
                raise Exception("Gateway not set in Web Connector")

        except Exception as e:
            log.error(f"Error processing Web message: {e}")
            return {"status": "error", "message": str(e)}

    # Funcion que me retorna el status de recibido del mensaje
    async def send_text_message(
        self, lead: WebLead, text: str, metadata: dict = {}, is_partial: bool = True
    ):
        """Envía un mensaje de texto parcial o completo y lo comunica al middleware.

        Args:
            - lead [WebLead]: Información del lead
            - text [str]: El texto a enviar
            - metadata [dict]: Metadatos del mensaje
            - is_partial [bool]: Indica si el mensaje es parcial
        """
        print("Are kidding me?")
        async with httpx.AsyncClient() as client:
            try:
                data = {
                    "conversation":f"{lead.session_id}",
                    "role": "assistant",
                    "content": text
                }
                print(self.web_url)
                response = await client.post(
                    f"{self.web_url}messages",
                    json=data
                )
                log.debug(f"response for the front: {response.status_code}")
            except Exception as e:
                log.error(f"Failed to send message to middleware: {e}")

    # Funcion que retorna el mensaje del bot
    async def send_select_message(
        self,
        lead: WebLead,
        text: str,
        options: List[str],
        metadata: dict = {},
        is_partial: bool = True,
    ):
        print(f"Bot: {text}")

    async def send_link_message(
        self,
        lead: WebLead,
        text: str,
        links: List[Dict[str, str]],
        metadata: dict = {},
        is_partial: bool = True,
    ):
        print(f"Bot: {text}")

    async def send_typing_action(self, lead: WebLead):
        log.warning("Sending typing action to Web is not implemented yet")

    async def send_message(self, message: OutgoingMessage):
        assert isinstance(
            message, OutgoingMessage
        ), "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, WebLead), "lead must be an instance of WebLead"
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

    def name(self) -> str:
        return "web"

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

        webhook_url = f"{context.webhook_url}{self.prefix}{self.endpoint}"
        log.debug(f"Starting Web connector with url: {webhook_url}")

    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down Web Connector")

    def pause(self):
        log.debug("Pausing Web Connector")
        self.paused = True

    def resume(self):
        log.debug("Resuming Web Connector")
        self.paused = False
