from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.responses import StreamingResponse
from typing import List, Annotated
from ..helpers.database import UUIDS
from uuid import UUID, uuid4
from ..helpers.response_models import SessionCreationIn, SessionCreationResponse, SessionGetAll, SessionGet
from hloc_server import datasets, DATABASE
import aiofiles

from sqlalchemy import select, update

DataSetRouter = APIRouter(
    prefix="/data",
    tags=["Dataset Upload"],
    responses={404: {"error": "Not found"}},
)


@DataSetRouter.post(
    "/upload/{uuid}",
    response_class=ORJSONResponse,
)
async def upload_data_set(uuid: UUID, images: Annotated[List[UploadFile], File(description="Multiple File Bytes")]):
    try:
        _session = select(UUIDS.c.dataset_dir, UUIDS.c.stop_data).where(UUIDS.c.uuid == str(uuid))
        _data = await DATABASE.fetch_one(_session)
        if _data[1]:
            return ORJSONResponse({"status": "Not Accepting images anymore"})
        session_dataset = datasets / _data[0]
        session_dataset_mapping = session_dataset / "mapping"
        await session_dataset_mapping.mkdir(parents=True, exist_ok=True)
        _new = 0
        for image in images:
            if image.content_type == "image/jpeg":
                async with aiofiles.open((session_dataset_mapping /
                                          (str(uuid4()) + "." + image.content_type.split("/")[1])),
                                         mode="wb"
                                         ) as img:
                    await img.write(await image.read())
                _new += 1
        _saved = 0
        async for _ in session_dataset_mapping.glob('*'):
            _saved += 1
        return ORJSONResponse(status_code=201, content={
            "no_of_files_already_present": _saved-_new,
            "no_of_files_sent": len(images),
            "new_files_saved": _new
        })
    except Exception as e:
        print(e)


@DataSetRouter.post(
    "/upload/stop/{uuid}",
    response_class=ORJSONResponse,
)
async def stop_accepting_data(uuid: UUID):
    try:
        _update_q = update(UUIDS).where(UUIDS.c.uuid == str(uuid)).values(stop_data=True)
        _data_dir = await DATABASE.execute(_update_q)
        return ORJSONResponse({"status": "New Image data will now be stopped"})
    except Exception as e:
        print(e)
