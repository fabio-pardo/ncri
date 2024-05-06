from fastapi import FastAPI

from app.api.data_filtering import data_filtering
from app.api.analytics import analytics

app = FastAPI()
app.include_router(data_filtering)
app.include_router(analytics)


@app.get("/")
async def root():
    return {"message": "Hello World"}
