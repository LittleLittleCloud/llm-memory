from ..model.document import PlainTextDocument
from .setup import EMBEDDING, STORAGE

def test_plain_text_document():
    doc = PlainTextDocument(
        name='test',
        description='test',
        url='contoso q&a.txt',
        embedding=EMBEDDING,
        storage=STORAGE,
    )
    records = doc.load_records()
    records = list(records)
    assert len(records) == 12
    assert records[-1].content.startswith('Return policies')
    assert records[0].meta_data['line_number'] == 0
    assert records[0].meta_data['document_id'] == 'test'
    assert records[0].meta_data['embedding_type'] == EMBEDDING.type


