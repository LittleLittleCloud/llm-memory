from ..model.document import PlainTextDocument
from .setup import EMBEDDING, STORAGE, SETTING
from ..index import QDrantVectorStore
from ..model.user import User
from qdrant_client import QdrantClient

def test_qdrant_vector_store():
    index = QDrantVectorStore(
        embedding=EMBEDDING,
        client= QdrantClient(
            url=SETTING.qdrant_url,
            api_key=SETTING.qdrant_api_key,),
        user=User(
            user_name='test_user',
            email='test@gmail.com',
            full_name='test user',
            disabled=False,),
        collection_name='test_collection',
    )

    index.create_collection_if_not_exists()
    assert index.if_collection_exists() == True

    # test load a new document
    contoso_qa = PlainTextDocument(
        embedding=EMBEDDING,
        storage=STORAGE,
        name='contoso q&a',
        description='contoso q&a',
        url='contoso q&a.txt',
    )

    index.load_or_update_document(contoso_qa)

    assert index.contains(contoso_qa) == True

    # test query document
    records = index.query_document(contoso_qa, 'return policy', 1)
    records = list(records)
    assert len(records) == 1
    assert records[0].content.startswith('Return policies')
    assert records[0].meta_data['line_number'] == 22
    assert records[0].meta_data['document_id'] == 'contoso q&a'
    assert records[0].meta_data['embedding_type'] == EMBEDDING.type

    # test query index
    records = index.query_index('return policy', 1)
    records = list(records)
    assert len(records) == 1
    assert records[0].content.startswith('Return policies')
    assert records[0].meta_data['line_number'] == 22
    assert records[0].meta_data['document_id'] == 'contoso q&a'
    assert records[0].meta_data['embedding_type'] == EMBEDDING.type

    # test remove document
    index.remove_document(contoso_qa)
    assert index.contains(contoso_qa) == False


