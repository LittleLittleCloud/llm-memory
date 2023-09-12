from storage import LocalStorage, Storage
from .setting import Settings
from .embedding import Embedding, OpenAITextAda002
from .index import Index, QDrantVectorStore
from .model.user import User
from qdrant_client import QdrantClient

SETTINGS: Settings = None
STORAGE: Storage = None
EMBEDDING: Embedding = None
INDEX: Index = None

def initialize_di_for_test() -> tuple[Settings, Storage,Embedding,Index]:
    global SETTINGS
    global STORAGE
    global EMBEDDING
    global INDEX

    SETTINGS = Settings(_env_file='./test/test.env')
    STORAGE = LocalStorage('./test/test_storage')
    EMBEDDING = OpenAITextAda002(SETTINGS.openai_api_key)
    INDEX = QDrantVectorStore(
        embedding=EMBEDDING,
        client= QdrantClient(
            url=SETTINGS.qdrant_url,
            api_key=SETTINGS.qdrant_api_key,),
        user=User(
            user_name='test_user',
            email='test@gmail.com',
            full_name='test user',
            disabled=False,
        ),
        collection_name='test_collection',
    )
    INDEX.create_collection_if_not_exists()

    return SETTINGS, STORAGE, EMBEDDING, INDEX

def initialize_di_for_prod() -> tuple[Settings, Storage,Embedding,Index]:
    global SETTINGS
    global STORAGE
    global EMBEDDING
    global INDEX

    SETTINGS = Settings(env_file='.env')
    STORAGE = LocalStorage('.local_storage')
    EMBEDDING = OpenAITextAda002(SETTINGS._env["OPENAI_API_KEY"])
    INDEX = QDrantVectorStore(
        _embedding=EMBEDDING,
        _client= QdrantClient(
            host=SETTINGS._env["QDRANT_HOST"],
            port=SETTINGS._env["QDRANT_PORT"],
            api_key=SETTINGS._env["QDRANT_API_KEY"],),
    )
    INDEX.create_collection_if_not_exists()

    return SETTINGS, STORAGE, EMBEDDING, INDEX