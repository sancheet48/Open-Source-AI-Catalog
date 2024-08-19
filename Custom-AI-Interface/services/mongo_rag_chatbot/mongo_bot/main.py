
import logging
import os
from logging.handlers import RotatingFileHandler


import fastapi
import uvicorn
from fastapi import Request
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from mongo_bot import const
from mongo_bot.routes import llm_bot




__version__ = "0.1.0"


logger = logging.getLogger(__file__)


API_BASE_PATH = "/api/v1"




def startup():
    """Startup method to check for environment variables."""
    if not os.path.isdir(os.path.join(const.PROJECT_DIR, "logs")):
        os.makedirs(os.path.join(const.PROJECT_DIR, "logs"), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(levelname)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                f"{os.path.join(const.PROJECT_DIR, 'logs', 'bot.log')}",
                maxBytes=256 * 1024,
                backupCount=10,
                encoding="utf8",
            ),
            logging.StreamHandler(),
        ],
    )
    logger.info("Deleting Proxies from the Env")
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if key in os.environ:
            del os.environ[key]




# Instantiate the FastApi application and add the custom schema to it
api = fastapi.FastAPI(
    title="EVF Server Query Bot",
    version=f"{__version__}",
    description="Chat with MongoDB Database.",
    contact={
        "name": "Sancheet Kumar Baidya",
        "email": "sancheet8baidya@gmail.com",
    },
    docs_url=None,
    on_startup=[startup],
)


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(llm_bot.bot_router)




@api.middleware("http")
async def req_res_middleware(request: Request, call_next):
    """Middleware to handle request and response.


    Args:
        request (Request): Request Object
        call_next (callable): Callback function


    Returns:
        response: Response Object
    """
    if request.url.path != "/health":
        logging.info("%s: %s", request.method, request.url)
    body = request.body if isinstance(request.body, dict) else {}
    if body and request.url.path != "/health":
        logging.info("Body: %s", body)
    try:
        response: Response = await call_next(request)
        if request.url.path != "/health":
            logging.info("Status Code: %s", response.status_code)
            response.headers["Strict-Transport-Security"] = (
                "max-age=1024000; includeSubDomains"
            )
        return response
    except Exception as excp:  # pylint: disable=broad-except
        logging.exception(excp)
        return JSONResponse(
            {"error": "Internal Server Error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )




@api.get("/", include_in_schema=False)
def index() -> fastapi.responses.RedirectResponse:
    """Route handler for root node of web server."""
    return fastapi.responses.RedirectResponse(url="./docs")




@api.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    """Override defaults docs page.


    Returns:
        any: Swagger UI HTML
    """
    root_path = request.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + api.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=api.title,
    )




@api.get(
    "/health",
    response_model=str,
    tags=["health"],
    responses={
        200: {"success": status.HTTP_200_OK},
    },
    include_in_schema=False,
)
def health():
    """


    """
    return JSONResponse(content="OK", status_code=status.HTTP_200_OK)




if __name__ == "__main__":
    uvicorn.run(api)