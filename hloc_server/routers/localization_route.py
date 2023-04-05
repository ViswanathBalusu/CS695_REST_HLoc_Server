from typing import Annotated

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.responses import StreamingResponse
from ..helpers.database import UUIDS
from uuid import UUID, uuid4
from ..helpers.response_models import SessionCreationIn, SessionCreationResponse, SessionGetAll, SessionGet

from hloc_server import outputs, datasets, DATABASE, SFM_PAIRS, LOC_PAIRS, SFM_DIR, FEATURES, MATCHES
from hloc_src.hloc import extract_features, match_features, reconstruction, visualization, pairs_from_exhaustive
from hloc_src.hloc.visualization import plot_images, read_image
from hloc_src.hloc.utils import viz_3d
from pycolmap import infer_camera_from_image
from hloc_src.hloc.localize_sfm import QueryLocalizer, pose_from_cluster
from sqlalchemy import select, update

LocalizeRouter = APIRouter(
    prefix="/localize/",
    tags=["Localization route"],
    responses={404: {"error": "Not found"}},
)


@LocalizeRouter.post(
    "/{uuid}",
    response_class=ORJSONResponse,
)
async def localize_image(uuid: UUID, image: Annotated[UploadFile, File(description="Upload the image that needs to be localized")]):
    try:
        _session = select(
            UUIDS.c.dataset_dir,
            UUIDS.c.extract_conf,
            UUIDS.c.matcher_conf,
            UUIDS.c.map_generated
        ).where(UUIDS.c.uuid == str(uuid))
        _data = await DATABASE.fetch_one(_session)
        if not _data[3]:
            return ORJSONResponse(content={"status": "Map already not generated"})
        _session_dataset = (datasets / str(_data[0]))
        _session_dataset_mapping = _session_dataset / "mapping"
        _session_query = _session_dataset / "query"
        await _session_query.mkdir(parents=True, exist_ok=True)
        if image.content_type != "image/jpeg":
            return ORJSONResponse(content={"status": " Only Jpeg files are accepted"})
        q_uuid = uuid4()
        _query = "query/" + (str(q_uuid) + "." + "jpeg")
        async with aiofiles.open(_query, mode="wb") as img:
            await img.write(await image.read())

        _session_outputs = outputs / str(uuid)
        _features = _session_outputs / FEATURES
        _matches = _session_outputs / MATCHES
        _sfm_pairs = _session_outputs / SFM_PAIRS
        _loc_pairs = _session_outputs / LOC_PAIRS
        _sfm_dir = _session_outputs / SFM_DIR

        feature_conf = extract_features.confs[_data[1]]
        matcher_conf = extract_features.confs[_data[2]]
        references = [path.relative_to(_session_dataset).as_posix()
                      async for path in _session_dataset_mapping.iterdir()]

        extract_features.main(feature_conf, _session_dataset, image_list=[_query], feature_path=_features, overwrite=True)
        pairs_from_exhaustive.main(_loc_pairs, image_list=[_query], ref_list=references)
        match_features.main(matcher_conf, _loc_pairs, features=_features, matches=_matches, overwrite=True)
        _camera = infer_camera_from_image(_session_dataset / _query)

    except Exception as e:
        print(e)
