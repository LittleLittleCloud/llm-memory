from .setup import EMBEDDING, STORAGE, SETTING
from ..embedding import OpenAITextAda002

def test_openai_text_ada_002():
    embedding = OpenAITextAda002(SETTING.openai_api_key)
    vector = embedding.generate_embedding('hello world')
    assert len(vector) == 1536
    assert embedding.type == 'text-ada-002'
    assert embedding.vector_size == 1536