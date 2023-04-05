
from databases import Database
from orm import ModelRegistry


__version__ = "0.0.1"
API_KEY = "test"
models = ModelRegistry(database=Database("sqlite:///./sessions.sqlite"))

