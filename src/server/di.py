from storage import LocalStorage, Storage
from setting import Settings
from embedding import Embedding, OpenAITextAda002
from index import Index, QDrantVectorStore
from model.user import User
from qdrant_client import QdrantClient

def initialize_di_for_test() -> tuple[Settings, Storage,Embedding,Index]:
    SETTINGS = Settings(_env_file='./test/test.env')
    STORAGE = LocalStorage('./test/test_storage')
    EMBEDDING = OpenAITextAda002(SETTINGS.openai_api_key)
    INDEX = QDrantVectorStore(
        embedding=EMBEDDING,
        client= QdrantClient(
            url=SETTINGS.qdrant_url,
            api_key=SETTINGS.qdrant_api_key,),
        
        collection_name='test_collection',
    )
    INDEX.create_collection_if_not_exists()

    return SETTINGS, STORAGE, EMBEDDING, INDEX

def initialize_di_for_app() -> tuple[Settings, Storage,Embedding,Index]:
    SETTINGS = Settings(_env_file='.env')
    STORAGE = LocalStorage('.local_storage')
    EMBEDDING = OpenAITextAda002(SETTINGS.openai_api_key)
    INDEX = QDrantVectorStore(
        embedding=EMBEDDING,
        client= QdrantClient(
            url=SETTINGS.qdrant_url,
            api_key=SETTINGS.qdrant_api_key,),
        collection_name='collection',
    )


    return SETTINGS, STORAGE, EMBEDDING, INDEX