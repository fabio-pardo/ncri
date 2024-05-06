from asyncpg.pool import Pool
from fastapi import Depends, FastAPI

from app.api.data_filtering import data_filtering
from app.db.database import get_db_pool_dependency

app = FastAPI()
app.include_router(data_filtering)


@app.get("/")
async def root(db_pool: Pool = Depends(get_db_pool_dependency)):
    return {"message": "Hello World"}
