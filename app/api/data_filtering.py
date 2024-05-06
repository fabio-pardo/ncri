from asyncpg.pool import Pool
from fastapi import APIRouter, Depends

from app.models.request.data_filtering import DataFilteringParams

data_filtering = APIRouter(
    prefix="/data_filtering", responses={404: {"description": "Not found"}}
)


@data_filtering.get("/")
async def root(
    data_filtering_params: DataFilteringParams,
):
    return data_filtering_params
