from orm import ModelRegistry
from databases import Database

sqlite_db = Database("sqlite:///test.sqlite")
models = ModelRegistry(database=sqlite_db)
