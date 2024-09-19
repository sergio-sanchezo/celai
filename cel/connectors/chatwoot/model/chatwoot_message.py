import time
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from .chatwoot_lead import ChatwootLead


class ChatwootMessage(Message):

    def __init__(
        self,
        lead: ConversationLead,
        text: str = None,
        metadata: dict = None,
        date: int = None,
    ):
        super().__init__(lead, text=text, date=date, metadata=metadata)

    def is_voice_message(self):
        return False

    @classmethod
    async def load_from_message(cls, message: dict, connector: BaseConnector = None):
        try:
            text = message.get("content")
            date = int(time.time())
            lead = ChatwootLead.from_chatwoot_message(message, connector=connector)
            return ChatwootMessage(lead=lead, text=text, date=date, metadata={"raw": message})
        except Exception as e:
            print("error has ocurred int load from message"+ e)

    def __str__(self):
        return f"WebMessage: {self.text}"

    def __repr__(self):
        return f"WebMessage: {self.text}"
