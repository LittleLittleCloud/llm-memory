from pydantic import BaseModel
from .record import Record
from ..storage import Storage
from ..embedding import Embedding
import time
from typing import ClassVar

class Document(BaseModel):
    name: str
    description: str | None = None
    status: str = 'uploading' # uploading, processing, done, failed
    url: str | None = None

    _embedding: Embedding
    _storage: Storage

    def load_records(self) -> list[Record]:
        pass

class PlainTextDocument(Document):
    def __init__(
            self,
            embedding: Embedding,
            storage: Storage,
            **kwargs):
        super().__init__(**kwargs)
        self._embedding = embedding
        self._storage = storage

    def load_records(self) -> list[Record]:
        bytes = self._storage.load(self.url)
        lines = bytes.decode('utf-8').split('\n')

        for i, line in enumerate(lines):
            # remove empty lines
            if len(line.strip()) == 0:
                continue
            embedding = self._embedding.generate_embedding(line)
            embedding_type = self._embedding.type
            meta_data = {
                'embedding_type': embedding_type,
                'document_id': self.name,
                'line_number': i,
            }

            yield Record(
                embedding=embedding,
                meta_data=meta_data,
                content=line,
                document_id=self.name,
                timestamp=int(time.time()))
