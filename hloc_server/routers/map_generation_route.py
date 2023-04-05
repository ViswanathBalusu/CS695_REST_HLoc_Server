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

from sqlalchemy import select, update

MapRouter = APIRouter(
    prefix="/map/",
    tags=["Feature Extraction and Mapping"],
    responses={404: {"error": "Not found"}},
)


@MapRouter.post(
    "/generate/{uuid}",
    response_class=ORJSONResponse,
)
async def generate_map(uuid: UUID):
    try:
        _session = select(
            UUIDS.c.dataset_dir,
            UUIDS.c.extract_conf,
            UUIDS.c.matcher_conf,
            UUIDS.c.map_generated
        ).where(UUIDS.c.uuid == str(uuid))
        _data = await DATABASE.fetch_one(_session)
        if _data[3]:
            return ORJSONResponse(content={"status": "Map already generated"})
        _no_images = 0
        _session_dataset = (datasets / str(_data[0]))
        _session_dataset_mapping = _session_dataset / "mapping"
        async for _ in _session_dataset.glob('*'):
            _no_images += 1
        if _no_images > 0:
            _session_outputs = outputs / str(uuid)
            await _session_outputs.mkdir(parents=True, exist_ok=True)
            _features = _session_outputs / FEATURES
            _matches = _session_outputs / MATCHES
            _sfm_pairs = _session_outputs / SFM_PAIRS
            _loc_pairs = _session_outputs / LOC_PAIRS
            _sfm_dir = _session_outputs / SFM_DIR

            feature_conf = extract_features.confs[_data[1]]
            matcher_conf = extract_features.confs[_data[2]]
            references = [path.relative_to(_session_dataset).as_posix()
                          async for path in _session_dataset_mapping.iterdir()]
            extract_features.main(feature_conf, _session_dataset, image_list=references, feature_path=_features)
            pairs_from_exhaustive.main(_sfm_pairs, image_list=references)
            match_features.main(matcher_conf, _sfm_pairs, features=_features, matches=_matches)
            reconstruction.main(_sfm_dir,
                                _session_dataset,
                                _sfm_pairs,
                                _features,
                                _matches,
                                image_list=references
                                )
            _update_q = update(UUIDS).where(UUIDS.c.uuid == str(uuid)).values(map_generated=True)
            await DATABASE.execute(_update_q)
            return ORJSONResponse(content={"status": "Extraction, Matching, SFM ran successfully, model generated and "
                                                     "saved"})
    except Exception as e:
        print(e)
