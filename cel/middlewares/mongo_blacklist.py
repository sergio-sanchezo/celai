from dataclasses import asdict
from loguru import logger as log
import time
from pymongo import MongoClient
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.middlewares.in_mem_blacklist import BlackListEntry

class MongoBlackListVapiMiddleware:
    """Middleware to block users based on a blacklist. The blacklist is stored in a MongoDB database."""

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "blacklistdb",
        collection_name: str = "blacklist",
    ):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def __call__(
        self, message: Message, connector: BaseConnector, assistant: BaseAssistant
    ):
        assert isinstance(message, Message), "Message must be a Message object"

        user_number = (
            message.lead.to_dict()
            .get("call_object", {})
            .get("customer", {})
            .get("number", "+56352280778")
        )
        log.warning(f"Checking if user {user_number} is blacklisted")

        id = user_number
        source = message.lead.connector_name

        entry = self.collection.find_one({"id": id})

        if entry:
            log.critical(
                f"User {id} from {source} is blacklisted. Reason: {entry['reason']}"
            )
            return (
                False,
                "Lamentablemente no puedo asistirlo con su consulta, por favor comuníquese al número 123",
            )
        else:
            return True

    def add_to_black_list(self, id: str, reason: str = None):
        entry = BlackListEntry(reason=reason, date=int(time.time()))
        self.collection.update_one(
            {"id": id},
            {"$set": {"id": id, **asdict(entry)}},
            upsert=True,
        )

    def remove_from_black_list(self, id: str):
        self.collection.delete_one({"id": id})

    def get_entry(self, id: str):
        entry = self.collection.find_one({"id": id})
        if entry:
            entry.pop("_id", None)
            return entry
        return None
