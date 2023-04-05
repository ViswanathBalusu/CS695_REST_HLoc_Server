from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class SessionCreationIn(BaseModel):
    name: str
    extractor_config: str
    matcher_config: str


class SessionCreationResponse(BaseModel):
    session_uuid: UUID


class SessionGet(BaseModel):
    uuid: UUID
    name: str
    extract_conf: str
    matcher_conf: str
    map_generated: bool
    time_added: str


class SessionGetAll(BaseModel):
    sessions_available: List[SessionGet]
