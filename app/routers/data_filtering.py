from asyncpg.pool import Pool
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.main import get_db_pool_dependency

data_filtering = APIRouter(
    prefix="/data_filtering", responses={404: {"description": "Not found"}}
)

content_types = {"all", "threatening", "non-threatening, hateful, neutral"}


class DataFilter(BaseModel):
    day: int
    week: int
    month: int
    content_type: Optional[str] = "all"

    @classmethod
    def validate_content_type(cls, content_type):
        content_types = {"threatening", "non-threatening", "hateful", "neutral"}
        if content_type is not None and content_type not in content_types:
            raise HTTPException(status_code=422, detail="Invalid content_type")
        return content_type

    @property
    def content_type_validated(self):
        return self.validate_content_type(self.content_type)


@data_filtering.get("/")
async def root(db_pool: Pool = Depends(get_db_pool_dependency)):
    pass
