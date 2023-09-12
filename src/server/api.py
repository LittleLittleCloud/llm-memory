import fastapi as api
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm
from model.document import Document, PlainTextDocument
import sys
from model.user import User
from fastapi import FastAPI, File, UploadFile
from di import initialize_di_for_app

SETTINGS, STORAGE, EMBEDDING, INDEX = initialize_di_for_app()

oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
app = api.FastAPI()
users = [
    User(
        user_name='bigmiao',
        email="g2260578356@gmail.com",
        documents=[],
        full_name="g2260578356",
        disabled=False)
]
async def get_current_user(token: str = api.Depends(oauth2_scheme)):
    '''
    Get current user
    '''
    for user in users:
        if user.user_name == token:
            return user
    
    raise api.HTTPException(status_code=401, detail="Invalid authentication credentials")


@app.post("/api/v1/auth/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, api.Depends()]):
    '''
    Login to get a token
    '''
    return {"access_token": form_data.username}

@app.post("/api/v1/uploadfile/")
async def create_upload_file(user: Annotated[User, api.Depends(get_current_user)], file: UploadFile = api.File(...)) -> Document:
    '''
    Upload a file
    '''
    fileUrl = f'{user.user_name}-{file.filename}'
    STORAGE.save(fileUrl, await file.read())

    # create plainTextDocument if the file is a text file
    if file.filename.endswith('.txt'):
        return PlainTextDocument(
            name=file.filename,
            status='uploading',
            url=fileUrl,
            embedding=EMBEDDING,
            storage=STORAGE,
        )
    else:
        raise api.HTTPException(status_code=400, detail="File type not supported")
        

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
    INDEX.load_or_update_document(user, document)
    document.status = 'done'
    user.documents.append(document)

#### Get /delete
# Delete a document
@app.get("/api/v1/document/delete")
async def delete_document(user: Annotated[User, api.Depends(get_current_user)], document_name: str):
    '''
    Delete a document
    '''
    for doc in user.documents:
        if doc.name == document_name:
            STORAGE.delete(doc.url)
            INDEX.remove_document(user, doc)
            user.documents.remove(doc)
            return
    
    raise api.HTTPException(status_code=404, detail="Document not found")

### /api/v1/query
#### Get query={query}&top_k={top_k}&threshold={threshold}
# Query the index
@app.get("/api/v1/query")
async def query_index(user: Annotated[User, api.Depends(get_current_user)], query: str, top_k: int = 10, threshold: float = 0.5):
    '''
    Query the index
    '''
    return INDEX.query_index(user, query, top_k, threshold)

#### Get query={query}&top_k={top_k}&threshold={threshold}&document={document}
# Query the document
@app.get("/api/v1/query/document")
async def query_document(user: Annotated[User, api.Depends(get_current_user)], query: str, top_k: int = 10, threshold: float = 0.5, document_name: str = None):
    '''
    Query the document
    '''

    # find the document
    for doc in user.documents:
        print(doc.name)
        if doc.name == document_name:
            return INDEX.query_document(user, doc, query, top_k, threshold)

    raise api.HTTPException(status_code=404, detail="Document not found")

def receive_signal(signalNumber, frame):
    print('Received:', signalNumber)
    sys.exit()


@app.on_event("startup")
async def startup_event():
    import signal
    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks