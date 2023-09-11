import openai

class Embedding:
    type: str|None = None
    vector_size: int|None = None
    def generate_embedding(self, content: str) -> list[float]:
        pass

class OpenAITextAda002(Embedding):
    type: str = 'text-ada-002'
    vector_size: int = 1536
    api_key: str = None

    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def generate_embedding(self, content: str) -> list[float]:
        # replace newline with space
        content = content.replace('\n', ' ')
        # limit to 8192 characters
        content = content[:6000]
        return openai.Embedding.create(
            input = content,
            model="text-embedding-ada-002"
        )["data"][0]["embedding"]
