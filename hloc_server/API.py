import time
from fastapi import FastAPI, Request, Security
from fastapi.responses import RedirectResponse

from hloc_server import __version__, models
from .helpers.api_key_helper import verify_api_key
from .routers.session_route import SessionRouter

HLoc = FastAPI(
    title="Hierarchical Localization",
    version=__version__,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/h_loc.json",
    dependencies=[Security(verify_api_key)],
)


@HLoc.on_event("startup")
async def database_init():
    await models.create_all()


#
@HLoc.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 3)) + " ms"
    return response


HLoc.include_router(SessionRouter)
