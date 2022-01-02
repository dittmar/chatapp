from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from databases import Database
from marshmallow import Schema, fields
from sqlalchemy import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.util.langhelpers import NoneType
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

@app.route("/users", methods=["POST"])
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

    query = message_table.select()
    try:
        data = await request.json()
        query = query.where(
            and_(
                message_table.columns.senderId==data["senderId"] if "senderId" in data else True,
                message_table.columns.receiverId==data["receiverId"] if "receiverId" in data else True
            )
        )
    except:
        pass

    results = await _database.fetch_all(query)
    content = [
        {
            "message": result["message"],
            "senderId": result["senderId"],
            "receiverId": result["receiverId"]
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

    print(data["message"])
    query = message_table.insert().values(
        message=data["message"],
        senderId=data["senderId"],
        receiverId=data["receiverId"] if "receiverId" in data else None
    )
    await _database.execute(query)
    return Response()

# For generating the OpenAPI schema
class UserParameter(Schema):
    username = fields.Str()

class SendMessageParameter(Schema):
    message = fields.Str()
    senderId = fields.Int()
    receiverId = fields.Int(nullable=True)

class ListMessageParameter(Schema):
    senderId = fields.Int(nullable=True)
    receiverId = fields.Int(nullable=True)

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