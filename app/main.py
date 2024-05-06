from fastapi import FastAPI

from app.api.data_filtering import data_filtering

app = FastAPI()
app.include_router(data_filtering)


@app.get("/")
async def root():
    return {"message": "Hello World"}
