from typing import List
from dataclasses import dataclass
from loguru import logger as log
import requests
from cel.rag.stores.vector_store import VectorStore, VectorRegister
from cel.rag.text2vec.utils import Embedding

@dataclass
class VectorRegisterResult(VectorRegister):
    """Vector register result for a backend service."""
    distance: float

class BackendStore(VectorStore):
    """Vector store that uses a backend service for embedding search.

    This store makes HTTP requests to a backend service to perform embedding search.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = None,
        account_id: str = None,
    ):
        """
        Args:
            base_url (str): The base URL of the backend service (e.g., 'http://localhost:3001')
            api_key (str): Optional API key or token for authorization
            account_id (str): Optional account identifier required by the backend service
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.account_id = account_id

    def search(self, query: str, top_k: int = 1) -> List[VectorRegister]:
        """Search for vectors similar to the query text.

        Args:
            query (str): The query text.
            top_k (int): The number of top results to return.

        Returns:
            List[VectorRegister]: A list of vector registers containing the results.
        """
        url = f"{self.base_url}/embeddings/search"
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "query": query,
            "topK": top_k,
        }
        if self.account_id:
            data["account"] = self.account_id

        log.debug(f"Making POST request to {url} with data: {data}")

        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 201:
            log.error(f"Error in search request: {response.status_code} {response.text}")
            response.raise_for_status()

        results = response.json()

        return [
            VectorRegisterResult(
                id=result["id"],
                vector=None,  # Vector is not returned; set to None
                text=result.get("text"),
                metadata=result.get("metadata"),
                distance=result.get("distance"),
            )
            for result in results
        ]

    def upsert(self, id: str, vector: Embedding, text: str, metadata: dict):
        """Not implemented, as embeddings are managed by the backend service."""
        raise NotImplementedError("Upsert is not supported in BackendStore.")

    def upsert_text(self, id: str, text: str, metadata: dict):
        """Not implemented, as embeddings are managed by the backend service."""
        raise NotImplementedError("Upsert text is not supported in BackendStore.")

    def delete(self, id: str):
        """Not implemented, as embeddings are managed by the backend service."""
        raise NotImplementedError("Delete is not supported in BackendStore.")

    def get_similar(self, vector: Embedding, top_k: int) -> List[VectorRegister]:
        """Not implemented, as embeddings are managed by the backend service."""
        raise NotImplementedError("Get similar is not supported in BackendStore.")

    def get_vector(self, id: str) -> VectorRegister:
        """Not implemented, as embeddings are managed by the backend service."""
        raise NotImplementedError("Get vector is not supported in BackendStore.")
