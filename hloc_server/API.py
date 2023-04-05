import time
from fastapi import FastAPI, Request, Security
from fastapi.responses import RedirectResponse

from hloc_server import __version__, DATABASE
from .helpers.api_key_helper import verify_api_key
from .routers.session_route import SessionRouter
from .routers.dataset_upload import DataSetRouter
from hloc_server import data, datasets, outputs

HLoc = FastAPI(
    title="Hierarchical Localization",
    version=__version__,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/h_loc.json",
    dependencies=[Security(verify_api_key)],
)


@HLoc.on_event("startup")
async def database_dir_init():
    await DATABASE.connect()
    await outputs.mkdir(parents=True, exist_ok=True)
    await datasets.mkdir(parents=True, exist_ok=True)


@HLoc.on_event("shutdown")
async def database_close():
    await DATABASE.disconnect()


#
@HLoc.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 3)) + " ms"
    return response


HLoc.include_router(SessionRouter)
HLoc.include_router(DataSetRouter)
