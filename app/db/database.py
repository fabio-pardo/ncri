from contextlib import asynccontextmanager

from asyncpg import create_pool
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://ncri:ncri@localhost:5432/ncri"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DBSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


# Would ideally use an environment config class to
# retrieve the following information
db_settings = DBSettings(
    host="localhost",  # postgres when in container, localhost in local
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
        if pool:
            await pool.close()


async def get_db_pool_dependency():
    async with get_db_pool(db_settings) as pool:
        yield pool
