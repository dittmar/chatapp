import databases
import sqlalchemy
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import UniqueConstraint
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.routing import Route

import chat_tables as tables

# Configuration from environment variables or '.env' file.
config = Config('.env')
DATABASE_URL = config('DATABASE_URL')

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

async def create_user(request):
    data = await request.json()
    query = tables.user_table.insert().values(
        username=data["username"]
    )
    await database.execute(query)
    return Response()

async def list_users(request):
    query = tables.user_table.select()
    results = await database.fetch_all(query)

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

routes = [
    Route("/users", endpoint=list_users, methods=["GET"]),
    Route("/users", endpoint=create_user, methods=["POST"])
]

app = Starlette(
    routes=routes,
    on_startup=[database.connect],
    on_shutdown=[database.disconnect]
)