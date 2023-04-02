import datetime
from uuid import uuid4
from orm import Model, UUID, String, DateTime
from hloc_server import models


class UUIDS(Model):
    tablename = "UUIDS"
    registry = models
    fields = {
        "id": UUID(title="uuid", primary_key=True, default=uuid4(), unique=True),
        "name": String(title="Name", max_length=64),
        "path": String(title="path_to_files", max_length=256),
        "time_added": DateTime(title="time_added", default=datetime.datetime.now(), read_only=True)
    }
