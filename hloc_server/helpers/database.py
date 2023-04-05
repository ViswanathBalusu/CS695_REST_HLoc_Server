import datetime

from orm import Model, UUID, String, DateTime, Boolean
from hloc_server import models
from uuid import uuid4

class UUIDS(Model):
    tablename = "UUIDS"
    registry = models
    fields = {
        "uuid": UUID(title="uuid", primary_key=True, default=uuid4()),
        "name": String(title="Name", max_length=64),
        "extract_conf": String(title="extract_conf", max_length=25),
        "matcher_conf": String(title="extract_conf", max_length=25),
        "map_generated": Boolean(title="map_generated", default=False),
        "time_added": DateTime(title="time_added", default=datetime.datetime.now(), read_only=True)
    }
