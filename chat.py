from apispec import APISpec
from databases import Database
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette_apispec import APISpecSchemaGenerator

from schema import user_table, message_table

# We need to import metadata so that the server will run happily
from schema import metadata

schemas = APISpecSchemaGenerator(
    APISpec(
        title="Chat API",
        version="1.0",
        openapi_version="3.0.2"
    )
)

# Configuration from environment variables or '.env' file.
_config = Config('.env')
DATABASE_URL = _config('DATABASE_URL')
_database = Database(DATABASE_URL)

app = Starlette(
    on_startup=[_database.connect],
    on_shutdown=[_database.disconnect]
)

@app.route("/schema", methods=["GET"], include_in_schema=False)
def schema(request):
    return schemas.OpenAPIResponse(request=request)

@app.route("/users", methods=["POST"])
async def create_user(request):
    """
        responses:
            200:
                description: user created successfully
            400:
                description: username already taken
        body:
            { "username": "some username" }
    """
    data = await request.json()
    # Return a Bad Request error if the username is already taken
    if await _database.fetch_one(user_table.select().where(user_table.columns.username == data["username"])):
        return Response(
            content="username already taken",
            status_code=400
        )
    query = user_table.insert().values(
        username=data["username"]
    )
    await _database.execute(query)
    return Response()

@app.route("/users", methods=["GET"])
async def list_users(request):
    """
        responses:
            200:
                description: return all users in the system
                examples:
                    [
                        {
                            "id": 1,
                            "username": "dittmar"
                        },
                        {
                            "id": 2,
                            "username": "storborg"
                        }
                    ]

    """
    query = user_table.select()
    results = await _database.fetch_all(query)

    content = [
        {
            "id": result["id"],
            "username": result["username"]
        }
        for result in results
    ]
    return JSONResponse(content)

#async def list_messages(request):
#    data = await request.json()
#    query = tables.message_table.select().where(
#        sqlalchemy.and_(
#            tables.message_table.columns.senderId==data['senderId'],
#            tables.message_table.columns.receiverId==data['receiverId']
#        )
#    )

#async def send_message(request):
#    data = await request.json()
#    query = tables.message_table.insert().values(
#        senderId=data["senderId"],
#        receiverId=data["receiverId"]
#    )

# Main application code.
#async def list_notes(request):
#    query = notes.select()
#    results = await database.fetch_all(query)
#    content = [
#        {
#            "text": result["text"],
#            "completed": result["completed"]
#        }
#        for result in results
#    ]
#    return JSONResponse(content)

#async def add_note(request):
#    data = await request.json()
#    query = notes.insert().values(
#       text=data["text"],
#       completed=data["completed"]
#    )
#    await database.execute(query)
#    return JSONResponse({
#        "text": data["text"],
#        "completed": data["completed"]
#    })