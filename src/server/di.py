from storage import LocalStorage, Storage
from .setting import Settings
from .embedding import Embedding, OpenAITextAda002
from .model.index import Index, QDrantVectorStore
from qdrant_client import QdrantClient

SETTINGS = Settings(env_file='.env')
STORAGE: Storage = LocalStorage('.local_storage')
EMBEDDING: Embedding = OpenAITextAda002(SETTINGS.env["OPENAI_API_KEY"])
INDEX: Index = QDrantVectorStore(
    embedding=EMBEDDING,
    client= QdrantClient(host=SETTINGS.env["QDRANT_HOST"], port=SETTINGS.env["QDRANT_PORT"]),
)