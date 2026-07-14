from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.database import Base, engine
from api.routers import scan, monitor, reports

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(monitor.router)
app.include_router(reports.router)


@app.get("/")
def read_root():
    return {"message": "SpySentinel API is running"}