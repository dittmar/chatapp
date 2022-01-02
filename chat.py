from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from databases import Database
from marshmallow import Schema, fields
from starlette.applications import Starlette
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette_apispec import APISpecSchemaGenerator

from schema import user_table, message_table

# We need to import metadata so that the server will run happily
from schema import metadata

# Configuration from environment variables or '.env' file.
_config = Config('.env')
DATABASE_URL = _config('DATABASE_URL')
_database = Database(DATABASE_URL)

app = Starlette(
    on_startup=[_database.connect],
    on_shutdown=[_database.disconnect]
)

@app.route("/users", methods=["GET"])
async def list_users(request):
    """
        responses:
            200:
                description: return all users in the system
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: integer
                                    username:
                                        type: string
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

@app.route("/users/login", methods=["POST"])
async def login(request: Request) -> Response:
    """
        requestBody:
            required: true
            content:
                application/json:
                    schema: UserParameter
        responses:
            200:
                description: user exists; logged in
                content:
                    application/json:
                        schema: UserResponse
            400:
                description: user does not exist
    """
    try:
        data = await request.json()
    except:
        return Response(
            content="no username given",
            status_code=400
        )
    user = await _database.fetch_one(user_table.select().where(user_table.columns.username == data["username"]))
    
    # Return a Bad Request error if the user does not exist
    if not user:
        return Response(
            content="user does not exist",
            status_code=400
        )

    # Convert the row into a JSON payload
    content = {}
    for column_name in map(lambda column: column.name, user_table.columns):
        content[column_name] = getattr(user, column_name)
    return JSONResponse(content)


@app.route("/users/create", methods=["POST"])
async def create_user(request: Request) -> Response:
    """
        requestBody:
            required: true
            content:
                application/json:
                    schema: UserParameter
        responses:
            200:
                description: user created successfully
            400:
                description: username already taken
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

# TODO (dittmar): This might need some tweaking and possibly to be separated into multiple endpoints
# to deal with global room, groups, and private messages better
@app.route("/messages/list", methods=["POST"])
async def list_messages(request: Request) -> JSONResponse:
    """
        requestBody:
            required: false
            content:
                application/json:
                    schema: ListMessageParameter
        responses:
            200:
                description: return all messages in the system
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: object
                                properties:
                                    message:
                                        type: string
                                    sender:
                                        type: string
                                    receiver:
                                        type: string
                                        nullable: true
    """

    # Use a raw SQL query because it's simpler than SQLAlchemy methods for this query
    query = """
    SELECT message, sender.username, receiver.username
    FROM messages
    LEFT JOIN users AS sender on sender.id = messages.senderId
    LEFT JOIN users AS receiver on receiver.id = messages.receiverId
    """

    try:
        data = await request.json()
        # If we have a senderId and/or a receiverId, we want to filter the messages returned
        # to only include ones for that sender and receiver pair
        query = query + "WHERE {} AND {}".format(
            "senderId = :senderId" if "senderId" in data else "TRUE",
            "receiverId = :receiverId" if "receiverId" in data else "TRUE"
        )
    except:
        data = {}
    results = await _database.fetch_all(query=query, values=data)

    content = [
        {
            "message": result[0],
            "senderId": result[1],
            "receiverId": result[2]
        }
        for result in results
    ]
    return JSONResponse(content)

@app.route("/messages/send", methods=["POST"])
async def send_message(request: Request) -> Response:
    """
        responses:
            200:
                description: message sent successfully
        requestBody:
            required: true
            content:
                application/json:
                    schema: SendMessageParameter
    """
    data = await request.json()

    query = message_table.insert().values(
        message=data["message"],
        senderId=data["senderId"],
        receiverId=data["receiverId"] if "receiverId" in data else None
    )
    await _database.execute(query)
    return Response()

# For generating the OpenAPI schema
class ListMessageParameter(Schema):
    senderId = fields.Int(nullable=True)
    receiverId = fields.Int(nullable=True)

class SendMessageParameter(Schema):
    message = fields.Str()
    senderId = fields.Int()
    receiverId = fields.Int(nullable=True)

class UserParameter(Schema):
    username = fields.Str()

class UserResponse(Schema):
    id = fields.Int()
    username = fields.Str()

schemas = APISpecSchemaGenerator(
    APISpec(
        title="Chat API",
        version="1.0",
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()]
    )
)

@app.route("/schema", methods=["GET"], include_in_schema=False)
def schema(request):
    return schemas.OpenAPIResponse(request=request)