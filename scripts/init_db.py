import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.db.database import Base, engine
from api.db import models

Base.metadata.create_all(bind=engine)
print("Database created successfully with tables:", Base.metadata.tables.keys())