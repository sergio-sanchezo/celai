import json
import time
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

    endpoint = "/message"

    def __init__(self, stream_mode: StreamMode = StreamMode.SENTENCE):
        log.debug("Creating Web connector")
        self.prefix = "/web"
        self.router = APIRouter(prefix=self.prefix)
        self.paused = False
        self.stream_mode = stream_mode
        self._create_routes(self.router)

    def _create_routes(self, router: APIRouter):
        @self.router.post(f"{WebConnector.endpoint}")
        async def chat_completion(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            background_tasks.add_task(self._process_message, data)
            return {"status": "ok"}

    async def _process_message(self, payload: Dict[str, Any]):
        try:
            log.debug("Received Web Message")
            log.debug(payload)
            msg = await WebMessage.load_from_message(payload, connector=self)

            if self.paused:
                log.warning("Connector is paused, ignoring message")
                return
            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass
            else:
                log.critical("Gateway not set in Web Connector")
                raise Exception("Gateway not set in Web Connector")

        except Exception as e:
            log.error(f"Error processing Web message: {e}")

    async def send_text_message(self, lead: WebLead, text: str, metadata: dict = {}, is_partial: bool = True):
        print(f"Bot: {text}")

    async def send_select_message(
        self, lead: WebLead, text: str, options: List[str], metadata: dict = {}, is_partial: bool = True
    ):
        print(f"Bot: {text}")

    async def send_link_message(
        self, lead: WebLead, text: str, links: List[Dict[str, str]], metadata: dict = {}, is_partial: bool = True
    ):
        print(f"Bot: {text}")

    async def send_typing_action(self, lead: WebLead):
        log.warning("Sending typing action to Web is not implemented yet")

    async def send_message(self, message: OutgoingMessage):
        assert isinstance(message, OutgoingMessage), "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, WebLead), "lead must be an instance of WebLead"
        lead = message.lead

        if message.type == OutgoingMessageType.TEXT:
            assert isinstance(message, OutgoingTextMessage), "message must be an instance of OutgoingTextMessage"
            await self.send_text_message(
                lead, message.content, metadata=message.metadata, is_partial=message.is_partial
            )

        if message.type == OutgoingMessageType.SELECT:
            assert isinstance(message, OutgoingSelectMessage), "message must be an instance of OutgoingSelectMessage"
            await self.send_select_message(
                lead, message.content, options=message.options, metadata=message.metadata, is_partial=message.is_partial
            )

        if message.type == OutgoingMessageType.LINK:
            assert isinstance(message, OutgoingLinkMessage), "message must be an instance of OutgoingLinkMessage"
            await self.send_link_message(
                lead, message.content, links=message.links, metadata=message.metadata, is_partial=message.is_partial
            )

    def name(self) -> str:
        return "web"

    def get_router(self) -> APIRouter:
        return self.router

    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway

        assert isinstance(gateway, MessageGateway), "gateway must be an instance of MessageGateway"
        self.gateway = gateway

    def startup(self, context: MessageGatewayContext):
        assert context.webhook_url, "webhook_url must be set in the context"
        assert context.webhook_url.startswith("https"),\
            f"webhook_url must be HTTPS, got: {context.webhook_url}.\
            Be sure that your url is public and has a valid SSL certificate."
        
        webhook_url = f"{context.webhook_url}{self.prefix}{WebConnector.endpoint}"
        log.debug(f"Starting Web connector with url: {webhook_url}")

    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down Web Connector")

    def pause(self):
        log.debug("Pausing Web Connector")
        self.paused = True

    def resume(self):
        log.debug("Resuming Web Connector")
        self.paused = False
