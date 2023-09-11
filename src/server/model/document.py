from pydantic import BaseModel
from .record import Record
from ..di import STORAGE, EMBEDDING
import time

class Document(BaseModel):
    name: str
    description: str | None = None
    status: str = 'uploading' # uploading, processing, done, failed
    url: str | None = None

    def load_records(self) -> list[Record]:
        pass

class PlainTextDocument(Document):
    def load_records(self) -> list[Record]:
        bytes = STORAGE.load(self.url)
        lines = bytes.decode('utf-8').split('\n')

        for i, line in enumerate(lines):
            embedding = EMBEDDING.generate_embedding(line)
            embedding_type = EMBEDDING.type
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
