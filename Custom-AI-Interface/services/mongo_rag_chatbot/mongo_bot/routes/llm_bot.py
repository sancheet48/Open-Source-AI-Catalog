"""Router for Elastic DB connect."""
import logging


import fastapi
from fastapi import Depends
from pydantic import BaseModel
from pydantic import Field
from mongo_bot import const
from mongo_bot.lib import bot
from mongo_bot.routes import validate_token




__version__ = "1.0.0"


logger = logging.getLogger(__file__)


bot_router = fastapi.APIRouter(
    prefix="/api/v1/bot",
    tags=["Query Bot"],
    on_startup=[bot.startup],
    on_shutdown=[bot.shutdown],
)




class BotQuery(BaseModel):
    """Model for querying LLM."""


    query: str = Field(..., max_length=150, title="Query string")




@bot_router.post(
    "/query",
    include_in_schema=True,
    response_model=None,
    dependencies=(
        [Depends(validate_token.verify_token)]
        if const.SERVICE_COM_TOKEN
        else []
    ),
)
def get_systems_from_query(bot_query: BotQuery) -> dict:
    """Get systems from query."""
    return bot.get_db_query(bot_query.query)
