from cel.rag.providers.rag_retriever import RAGRetriever
from cel.rag.stores.vector_store import VectorRegister, VectorStore
from cel.model.common import ContextMessage

class CustomRAGRetriever(RAGRetriever):
    def __init__(self, store: VectorStore):
        self.store = store

    def search(
        self,
        query: str,
        top_k: int = 1,
        history: list[ContextMessage] = None,
        state: dict = {}
    ) -> list[VectorRegister]:
        return self.store.search(query, top_k)