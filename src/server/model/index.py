from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint

from ..embedding import Embedding
from .document import Document
from .record import Record
from .user import User
from ..di import STORAGE, EMBEDDING
from qdrant_client.http import models
import uuid
import json

class Index(BaseModel):
    user: User
    type: str
    name: str
    description: str | None = None

    def load_or_update_document(self, document: Document):
        pass

    def remove_document(self, document: Document):
        pass
    
    def query_index(self, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        pass

    def query_document(self, document: Document, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        pass

class QDrantVectorStore(Index):
    client: QdrantClient
    embedding: Embedding
    collection_name: str
    batch_size: int = 10


    def _response_to_records(self, response: list[ScoredPoint]) -> list[Record]:
        for point in response:
            meta_data = json.loads(point.payload['meta_data'])
            yield Record(
                embedding=point.vector,
                meta_data= meta_data,
                content=point.payload['content'],
                document_id=point.payload['document_id'],
                timestamp=meta_data['timestamp'],
            )

    def create_collection(self):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(self.embedding.vector_size, distance=models.Distance.COSINE),
            extra_params={
                'meta': {
                    'embedding_type': self.embedding.type,
                }
            }
        )

    def if_collection_exists(self) -> bool:
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False
        
    def create_collection_if_not_exists(self):
        if not self.if_collection_exists():
            self.create_collection()

    def load_or_update_document(self, document: Document):
        self.create_collection_if_not_exists()

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
                'user_id': self.user.user_name,
            } for record in batch]
            vectors = [record.embedding for record in batch]
            self.client.upsert(
                collection_name=self.collection_name,
                payload=payloads,
                ids=uuids,
                vectors=vectors,
                ids_field='id',
                extra_params={
                    'group_id': group_id,
                    'document_id': document.name,
                }
            )
    
    def remove_document(self, document: Document):
        if not self.if_collection_exists():
            return
        
        document_id = document.name
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        ),
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=self.user.user_name)
                        ),
                    ]
                )
            )
        )

    def query_index(self, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        if not self.if_collection_exists():
            return []
        
        response = self.client.search(
            collection_name=self.collection_name,
            query_vector=self.embedding.generate_embedding(query),
            limit=top_k,
            query_filter=[
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=self.user.user_name)
                        ),
                    ]
                )
            ],
            score_threshold=threshold,
        )

        return self._response_to_records(response)
    
    def query_document(self, document: Document, query: str, top_k: int = 10, threshold: float = 0.5) -> list[Record]:
        if not self.if_collection_exists():
            return []
        
        response = self.client.search(
            collection_name=self.collection_name,
            query_vector=self.embedding.generate_embedding(query),
            limit=top_k,
            query_filter=[
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=self.user.user_name)
                        ),
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document.name)
                        ),
                    ]
                )
            ],
            score_threshold=threshold,
        )

        return self._response_to_records(response)
            