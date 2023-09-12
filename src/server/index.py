from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint

from .embedding import Embedding
from .model.document import Document
from .model.record import Record
from .model.user import User
from qdrant_client.http import models
import uuid
import json

class Index:
    user: User
    type: str

    def load_or_update_document(self, document: Document):
        pass

    def remove_document(self, document: Document):
        pass
    
    def query_index(self, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        pass

    def query_document(self, document: Document, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        pass

    def contains(self, document: Document) -> bool:
        pass

class QDrantVectorStore(Index):
    _client: QdrantClient
    _embedding: Embedding
    collection_name: str
    batch_size: int = 10
    type: str = 'qdrant'

    def __init__(
            self,
            user: User,
            client: QdrantClient,
            embedding: Embedding,
            collection_name: str):
        self.user = user
        self._embedding = embedding
        self.collection_name = collection_name
        self._client = client

    def _response_to_records(self, response: list[ScoredPoint]) -> list[Record]:
        for point in response:
            meta_data = point.payload['meta_data']
            yield Record(
                embedding=point.vector,
                meta_data= meta_data,
                content=point.payload['content'],
                document_id=point.payload['document_id'],
                timestamp=point.payload['timestamp'],
            )

    def create_collection(self):
        self._client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self._embedding.vector_size,
                distance=models.Distance.COSINE),
        )

    def if_collection_exists(self) -> bool:
        try:
            self._client.get_collection(self.collection_name)
            return True
        except Exception:
            return False
        
    def create_collection_if_not_exists(self):
        if not self.if_collection_exists():
            self.create_collection()

    def load_or_update_document(self, document: Document):
        self.create_collection_if_not_exists()

        if self.contains(document):
            self.remove_document(document)

        group_id = self.user.user_name
        # upsert records in batch
        records = document.load_records()
        records = list(records)
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i+self.batch_size]
            uuids = [str(uuid.uuid4()) for _ in batch]
            payloads = [{
                'content': record.content,
                'meta_data': record.meta_data,
                'document_id': record.document_id,
                'group_id': group_id,
                'timestamp': record.timestamp,
            } for record in batch]
            vectors = [record.embedding for record in batch]
            self._client.upsert(
                collection_name=self.collection_name,
                points=models.Batch(
                    payloads=payloads,
                    ids=uuids,
                    vectors=vectors,
                ),
            )
    
    def remove_document(self, document: Document):
        if not self.if_collection_exists():
            return
        
        document_id = document.name
        self._client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        ),
                        models.FieldCondition(
                            key="group_id",
                            match=models.MatchValue(
                            value=self.user.user_name,
                            ),
                        )
                    ]
                )
            )
        )

    def contains(self, document: Document) -> bool:
        document_id = document.name
        group_id = self.user.user_name

        count = self._client.count(
            collection_name=self.collection_name,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id)
                    ),
                    models.FieldCondition(
                        key="group_id",
                        match=models.MatchValue(
                        value=group_id,
                        ),
                    )
                ]
            ),
            exact=True,
        )

        return count.count > 0

    def query_index(self, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        if not self.if_collection_exists():
            return []
        
        response = self._client.search(
            collection_name=self.collection_name,
            query_vector=self._embedding.generate_embedding(query),
            limit=top_k,
            query_filter= models.Filter(
                must=[
                    models.FieldCondition(
                        key="group_id",
                        match=models.MatchValue(
                        value=self.user.user_name,
                        ),
                    )
                ]
            ),
            score_threshold=threshold,
        )

        return self._response_to_records(response)
    
    def query_document(self, document: Document, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        if not self.if_collection_exists():
            return []
        
        response = self._client.search(
            collection_name=self.collection_name,
            query_vector=self._embedding.generate_embedding(query),
            limit=top_k,
            query_filter= models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document.name)
                    ),
                    models.FieldCondition(
                        key="group_id",
                        match=models.MatchValue(value=self.user.user_name),
                    )
                ]
            ),
            score_threshold=threshold,
        )

        return self._response_to_records(response)
            