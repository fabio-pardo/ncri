from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from asyncpg import create_pool
from asyncpg.pool import Pool
from pydantic import BaseModel

app = FastAPI()


class DBSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


db_settings = DBSettings(
    host="postgres",
    port=5432,  # Default PostgreSQL port
    user="ncri",
    password="ncri",
    database="ncri",
)


@asynccontextmanager
async def get_db_pool(settings: DBSettings):
    pool = await create_pool(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        database=settings.database,
    )
    try:
        yield pool
    finally:
        await pool.close()


async def get_db_pool_dependency():
    async with get_db_pool(db_settings) as pool:
        yield pool


@app.get("/")
async def root(db_pool: Pool = Depends(get_db_pool_dependency)):
    return {"message": "Hello World"}
