import fastapi as api
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm
from model.document import Document
from model.user import User
from fastapi import FastAPI, File, UploadFile
from .di import STORAGE, INDEX

oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
app = api.FastAPI()

async def get_current_user(token: str = api.Depends(oauth2_scheme)):
    '''
    Get current user
    '''
    return User(user_name=token, email="g2260578356@gmail.com", full_name="g2260578356", disabled=False)

@app.post("/api/v1/auth/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, api.Depends()]):
    '''
    Login to get a token
    '''
    return {"access_token": form_data.username + "token"}

@app.post("/api/v1/uploadfile/")
async def create_upload_file(user: Annotated[User, api.Depends(get_current_user)], file: UploadFile = api.File(...)) -> Document:
    '''
    Upload a file
    '''
    fileUrl = f'{user.user_name}-{file.filename}'
    await STORAGE.save(fileUrl, await file.read())
    return Document(name=file.filename, status='uploading', url=fileUrl)

### /api/v1/.well-known
#### Get /openapi.json
# Get the openapi json file
@app.get("/api/v1/.well-known/openapi.json")
async def get_openapi(user: Annotated[User, api.Depends(get_current_user)]):
    '''
    Get the openapi json file if user is authenticated
    otherwise return 401
    '''

### /api/v1/document
#### Get /list
# Get the list of documents
@app.get("/api/v1/document/list")
async def get_document_list(user: Annotated[User, api.Depends(get_current_user)]) -> list[Document]:
    '''
    Get the list of documents
    '''
    return user.documents

#### Post /upload
# Upload a document
@app.post("/api/v1/document/upload")
async def upload_document(user: Annotated[User, api.Depends(get_current_user)], document: Annotated[Document, api.Depends(create_upload_file)]):
    '''
    Upload a document
    '''
    document.status = 'processing'
    INDEX.load_or_update_document(document)
    document.status = 'done'
    user.documents.append(document)

#### Get /delete
# Delete a document
@app.get("/api/v1/document/delete")
async def delete_document(user: Annotated[User, api.Depends(get_current_user)], document: Document):
    '''
    Delete a document
    '''
    await STORAGE.delete(document.url)
    INDEX.remove_document(document)
    user.documents.remove(document)

### /api/v1/query
#### Get query={query}&top_k={top_k}&threshold={threshold}
# Query the index
@app.get("/api/v1/query")
async def query_index(user: Annotated[User, api.Depends(get_current_user)], query: str, top_k: int = 10, threshold: float = 0.5):
    '''
    Query the index
    '''
    return INDEX.query_index(query, top_k, threshold)

#### Get query={query}&top_k={top_k}&threshold={threshold}&document={document}
# Query the document
@app.get("/api/v1/query/document")
async def query_document(user: Annotated[User, api.Depends(get_current_user)], query: str, top_k: int = 10, threshold: float = 0.5, document_name: str = None):
    '''
    Query the document
    '''

    # find the document
    for doc in user.documents:
        if doc.name == document_name:
            return INDEX.query_document(doc, query, top_k, threshold)

    raise api.HTTPException(status_code=404, detail="Document not found")

