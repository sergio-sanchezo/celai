from abc import ABC
from dataclasses import dataclass
from loguru import logger as log
from pymongo import MongoClient
from pymongo.collection import Collection
from cel.rag.stores.vector_store import VectorRegister, VectorStore
from cel.rag.text2vec.utils import Embedding, Text2VectorProvider

@dataclass
class VectorRegisterResult(VectorRegister):
    """Vector register for MongoDBStore"""
    distance: float

class MongoDBStore(VectorStore):
    def __init__(
        self,
        text2vec_provider: Text2VectorProvider,
        collection_name: str = "my_collection",
        db_name: str = "my_db",
        mongo_uri: str = "mongodb://localhost:27017",
    ):
        log.debug(f"Instantiate MongoDBStore with collection_name: {collection_name}")
        self.text2vec = text2vec_provider
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection_name = collection_name
        self.collection: Collection = self.db[collection_name]

        # Note: Vector index creation is handled via Atlas Search index definitions, not via pymongo.

    def get_vector(self, id: str) -> VectorRegister:
        """Get a vector from MongoDB by id"""
        doc = self.collection.find_one({"_id": id})
        if doc:
            return VectorRegister(
                id=doc["_id"],
                vector=doc["vector"],
                text=doc["text"],
                metadata=doc["metadata"],
            )
        else:
            raise KeyError(f"No document found with id: {id}")

    def get_similar(self, vector: Embedding, top_k: int) -> list[VectorRegisterResult]:
        """Get the most similar vectors to the given vector"""
        pipeline = [
            {
                "$search": {
                    "knn": {
                        "vector": vector,
                        "path": "vector",
                        "k": top_k,
                    }
                }
            },
            {"$limit": top_k},
            {
                "$project": {
                    "_id": 1,
                    "text": 1,
                    "metadata": 1,
                    "vector": 1,
                    "score": {"$meta": "searchScore"},
                }
            },
        ]
        results = self.collection.aggregate(pipeline)
        return [
            VectorRegisterResult(
                id=doc["_id"],
                vector=doc["vector"],
                distance=doc["score"],
                text=doc["text"],
                metadata=doc["metadata"],
            )
            for doc in results
        ]

    def search(self, query: str, top_k: int = 1) -> list[VectorRegisterResult]:
        """Search for vectors by a query"""
        vector = self.text2vec.text2vec(query)
        return self.get_similar(vector, top_k)

    def upsert(self, id: str, vector: Embedding, text: str, metadata: dict):
        """Upsert a vector to the store"""
        try:
            self.collection.replace_one(
                {"_id": id},
                {
                    "_id": id,
                    "vector": vector,
                    "text": text,
                    "metadata": metadata,
                },
                upsert=True,
            )
        except Exception as e:
            log.error(f"Error upserting document with id {id}: {e}")

    def upsert_text(self, id: str, text: str, metadata: dict):
        """Upsert a text document and its vector to the store"""
        vector = self.text2vec.text2vec(text)
        self.upsert(id, vector, text, metadata)

    def delete(self, id):
        """Delete a vector from the store"""
        self.collection.delete_one({"_id": id})
