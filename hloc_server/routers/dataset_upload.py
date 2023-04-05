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

from sqlalchemy import select

DataSetRouter = APIRouter(
    prefix="/data",
    tags=["Dataset Upload"],
    responses={404: {"error": "Not found"}},
)


@DataSetRouter.post(
    "/upload/{uuid}",
    response_class=ORJSONResponse,
    # response_model=SessionCreationResponse
)
async def upload_data_set(uuid: UUID, images: Annotated[List[UploadFile], File(description="Multiple File Bytes")]):
    try:
        old_session_uuid = select(UUIDS.c.dataset_dir).where(UUIDS.c.uuid == str(uuid))
        _data_dir = await DATABASE.fetch_val(old_session_uuid)
        session_dataset = datasets / _data_dir
        await session_dataset.mkdir(parents=True, exist_ok=True)
        for image in images:
            async with aiofiles.open((session_dataset / (str(uuid4()) + ".png")), mode="wb") as img:
                await img.write(await image.read())

        # return ORJSONResponse(content={"no_images": len(images)})
        return {"filenames": [file.filename for file in images]}
    except Exception as e:
        print(e)
