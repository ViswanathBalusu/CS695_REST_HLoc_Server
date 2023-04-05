from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.responses import StreamingResponse
from ..helpers.database import UUIDS
from uuid import UUID, uuid4
from ..helpers.response_models import SessionCreationIn, SessionCreationResponse, SessionGetAll

SessionRouter = APIRouter(
    prefix="/session",
    tags=["Sessions"],
    responses={404: {"error": "Not found"}},
)


@SessionRouter.post(
    "/create",
    response_class=ORJSONResponse,
    response_model=SessionCreationResponse
)
async def get_a_session(session_config: SessionCreationIn):
    try:
        _uuid = uuid4()
        test = await UUIDS.objects.create(
            name=session_config.name,
            uuid=_uuid,
            extract_conf=session_config.extractor_config,
            matcher_conf=session_config.matcher_config
        )
        return ORJSONResponse(content={"session_uuid": _uuid})
    except Exception as e:
        print(e)


@SessionRouter.delete(
    "/{uuid}",
    response_class=ORJSONResponse,
    response_model=SessionCreationResponse
)
async def delete_session(uuid: UUID):
    try:
        await UUIDS.objects.filter(uuid=uuid).delete()
        return ORJSONResponse(content={"session_uuid": uuid})
    except Exception as e:
        print(e)


@SessionRouter.delete(
    "/{uuid}",
    response_class=ORJSONResponse,
    response_model=SessionCreationResponse
)
async def delete_session(uuid: UUID):
    try:
        await UUIDS.objects.filter(uuid=uuid).delete()
        return ORJSONResponse(content={"session_uuid": uuid})
    except Exception as e:
        print(e)

@SessionRouter.get(
    "/all",
    response_class=ORJSONResponse,
    response_model=SessionGetAll
)
async def get_all_sessions():
    try:
        _all = await UUIDS.objects.all()
        return ORJSONResponse(content={"sessions": [jsonable_encoder(item) for item in _all]})
    except Exception as e:
        print(e)


@SessionRouter.delete(
    "/all",
    response_class=ORJSONResponse,
    response_model=SessionGetAll
)
async def delete_all_sessions():
    try:
        _all = await UUIDS.objects.all()
        return ORJSONResponse(content={"sessions": [jsonable_encoder(item) for item in _all]})
    except Exception as e:
        print(e)
