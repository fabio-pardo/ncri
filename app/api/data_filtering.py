from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.tweets import Tweet
from app.models.request.data_filtering import (
    HATEFUL,
    NEUTRAL,
    NON_THREATENING,
    THREATENING,
    DataFilteringParams,
)

data_filtering = APIRouter(
    prefix="/data_filtering",
    responses={
        404: {"description": "Not found"},
    },
)


@data_filtering.post("/twitter/")
async def get_filtered_data(
    data_filtering_params: DataFilteringParams,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves filtered data from the Twitter dataset based on the provided filtering parameters. Users can filter the data based on day, month, and year, as well as the content type of the tweets, including threatening, non-threatening, neutral, or hateful content.

    Parameters:
    - data_filtering_params: Object containing filtering parameters including day, month, year, and content_type_validated.
    - page: Page number for pagination.
    - page_size: Number of results per page. Must be between 1 and 100, inclusive.

    Response:
    - tweets: Filtered tweets based on the provided parameters.
    - total_tweets: Total count of tweets matching the filtering criteria.
    """

    query = db.query(Tweet)
    # Apply filters based on provided parameters
    if data_filtering_params.day:
        query = query.filter(Tweet.day == data_filtering_params.day)
    if data_filtering_params.month:
        query = query.filter(Tweet.month == data_filtering_params.month)
    if data_filtering_params.year:
        query = query.filter(Tweet.year == data_filtering_params.year)
    if content_type := data_filtering_params.content_type_validated:
        # NOTE: these filters could be moved out.
        threatening_filter = or_(
            Tweet.threat_level == "Medium",
            Tweet.threat_level == "High",
        )
        non_threatening_filter = or_(
            Tweet.threat_level == "Low",
            Tweet.threat_level.is_(None),
        )
        hateful_filter = or_(
            Tweet.hateful == "Medium",
            Tweet.hateful == "High",
        )
        non_hateful_filter = or_(
            Tweet.hateful == "Low",
            Tweet.hateful.is_(None),
        )
        if content_type == THREATENING:
            query = query.filter(threatening_filter)
        elif content_type == NON_THREATENING:
            query = query.filter(non_threatening_filter)
        elif content_type == HATEFUL:
            query = query.filter(hateful_filter)
        elif content_type == NEUTRAL:
            query.filter(
                and_(
                    non_threatening_filter,
                    non_hateful_filter,
                )
            )
        else:
            raise NotImplementedError

    # Apply pagination
    # NOTE: Including this here only for quickness.
    # Because other routes will use this functionality,
    # I'd move this elesewhere.
    total_tweets = query.count()
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute the query and return results
    filtered_tweets = query.all()

    return {
        "tweets": filtered_tweets,
        "total_tweets": total_tweets,
    }
