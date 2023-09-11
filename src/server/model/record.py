from pydantic import BaseModel

class Record(BaseModel):
    content: str
    embedding: list[float] | None = None
    document_id: str | None = None
    meta_data: dict | None = None
    timestamp: int | None = None
