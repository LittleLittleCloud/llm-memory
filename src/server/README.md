A fastapi server for llm-memory

## api
### /api/v1/login
#### Post /
Login with username and password

### /api/v1/user
#### Get /{id}
Get a user by id

#### Post /
Create a new user

### /api/v1/query?query={query}&k={k}&threshold={threshold}
#### Get
Get a list of query result

### /api/v1/document
#### Get /list
Get a list of all documents

#### Get /{id}
Get a document by id

#### Post /
Create a new document

#### Delete /{id}
Delete a document by id

### /api/v1/.well-known
#### Get /openapi.json
Get the openapi json file
