from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class ChatwootLead(ConversationLead):

    def __init__(self, session_id: str, **kwargs):
        super().__init__(connector_name="chatwoot", **kwargs)
        self.session_id = session_id

    def get_session_id(self):
        return f"{self.connector_name}:{self.session_id}"

    def to_dict(self):
        data = super().to_dict()
        data["session_id"] = self.session_id
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return ChatwootLead(
            session_id=lead_dict.get("session_id"), 
            metadata=lead_dict.get("metadata")
        )

    def __str__(self):
        return f"ChatwootLead: {self.session_id}"

    @classmethod
    def from_chatwoot_message(cls, message: dict, **kwargs):
        try:
            assert isinstance(message, dict), "data must be a dictionary"
            print(message,'from_chatwoot_message')
            session_id = str(message.get("conversation"))
            conversation_peer = ConversationPeer(
                name=message.get("name", "unknown"),
                id=session_id,
                phone=None,
                avatarUrl=None,
                email=None,
            )
            return ChatwootLead(
                session_id=session_id, conversation_from=conversation_peer, **kwargs
            )
        except Exception as e:
            print("occurred in from_chatwoot_message: " + e)
