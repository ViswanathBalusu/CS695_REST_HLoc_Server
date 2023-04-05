from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.responses import StreamingResponse
from ..helpers.database import UUIDS
from uuid import UUID, uuid4
from ..helpers.response_models import SessionCreationIn, SessionCreationResponse, SessionGetAll, SessionGet

SessionRouter = APIRouter(
    prefix="/upload/",
    tags=["Sessions"],
    responses={404: {"error": "Not found"}},
)