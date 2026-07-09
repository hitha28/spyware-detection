from fastapi import FastAPI

from api.db.database import Base, engine
from api.routers import scan

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(scan.router)


@app.get("/")
def read_root():
    return {"message": "SpySentinel API is running"}