import datetime

from orm import Model, UUID, String, DateTime, Boolean, Integer
from hloc_server import DB_URL

import sqlalchemy

from uuid import uuid4

metadata = sqlalchemy.MetaData()


UUIDS = sqlalchemy.Table(
    "UUIDS",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.String(40), primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(30)),
    sqlalchemy.Column("extract_conf", sqlalchemy.String(20)),
    sqlalchemy.Column("matcher_conf", sqlalchemy.String(20)),
    sqlalchemy.Column("dataset_dir", sqlalchemy.String(40)),
    sqlalchemy.Column("map_generated", sqlalchemy.Boolean),
    sqlalchemy.Column("time_added", sqlalchemy.DateTime)
)

engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

# class UUIDS(Model):
#     tablename = "UUIDS"
#     registry = models
#     fields = {
#         "id": Integer(primary_key=True),
#         "uuid": UUID(title="uuid"),
#         "name": String(title="name", max_length=64),
#         "extract_conf": String(title="extract_conf", max_length=25),
#         "dataset_dir": UUID(title="dataset_dir", default=uuid4()),
#         "matcher_conf": String(title="matcher_conf", max_length=25),
#         "map_generated": Boolean(title="map_generated", default=False),
#         "time_added": DateTime(title="time_added", default=datetime.datetime.now(), read_only=True)
#     }
