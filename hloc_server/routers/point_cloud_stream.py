import json

import aiofiles
import orjson
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, JSONResponse
from ..helpers.database import UUIDS
from uuid import UUID, uuid4
from typing import List

from hloc_server import outputs, DATABASE, SFM_DIR
from ..helpers.point_cloud import get_point_cloud, NDArrayEncoder
from sqlalchemy import select
from pathlib import Path

PointCloudRouter = APIRouter(
    prefix="/pointcloud",
    tags=["Point Cloud route"],
    responses={404: {"error": "Not found"}},
)


@PointCloudRouter.post(
    "/{uuid}",
)
@PointCloudRouter.get(
    "/{uuid}",
)
async def point_cloud_get(uuid: UUID):
    try:
        _session = select(
            UUIDS.c.map_generated,
            UUIDS.c.sfm_uploaded
        ).where(UUIDS.c.uuid == str(uuid))
        _data = await DATABASE.fetch_one(_session)
        if not _data[1]:
            if not _data[0]:
                return ORJSONResponse(content={"status": "Map not already Uploaded or generated"})
        _session_outputs = outputs / str(uuid)
        _sfm_dir = Path(_session_outputs / SFM_DIR)
        points_pos = get_point_cloud(_sfm_dir)
        return ORJSONResponse(content={"db_points_pos": points_pos.tolist()}
                              )
    except Exception as e:
        print(str(e))
