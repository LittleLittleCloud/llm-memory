from pydantic import BaseModel
from .document import Document

class User(BaseModel):
    user_name: str
    email: str
    full_name: str
    disabled: bool = None

    documents: list[Document] = None


    