from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.limiter import limiter

from app.db.database import get_db
from app.db.models.tweets import Tweet
from app.models.request.data_filtering import HATEFUL, THREATENING

analytics = APIRouter(
    prefix="/analytics",
    responses={
        404: {"description": "Not found"},
    },
)


@analytics.get("/twitter/users/stats")
@limiter.limit("5/minute")
async def get_key_user_stats(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves statistics about key users in the Twitter dataset, including the count of tweets posted by each user. The results are sorted in descending order based on the tweet count.

    Parameters:
    - page: Page number for pagination.
    - page_size: Number of key users to include per page. Must be between 1 and 100, inclusive.

    Response:
    - total_count: Total count of key users in the dataset.
    - items: A list containing information about key users, including their username (author) and the count of tweets posted by each user.
    """
    # Calculate offset based on page number and page size
    offset = (page - 1) * page_size

    # Query for total count of key users
    total_count_query = db.query(func.count(func.distinct(Tweet.author)))
    total_count = total_count_query.scalar()

    # Query for key users with pagination
    query = (
        db.query(Tweet.author, func.count().label("tweet_count"))
        .group_by(Tweet.author)
        .order_by(func.count().desc())
        .limit(page_size)
        .offset(offset)
    )

    # Execute the query and convert results to a list of dictionaries
    result = [{"author": row.author, "tweet_count": row.tweet_count} for row in query]

    return {"total_count": total_count, "items": result}


@analytics.get("/twitter/stats")
@limiter.limit("5/minute")
async def get_specific_tweet_stats(
    request: Request,
    start_date: Optional[datetime] = Query(default=None, description="Start date"),
    end_date: Optional[datetime] = Query(default=None, description="End date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    criteria: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves specific Twitter statistics based on the set time interval and optional criteria. By default, it returns statistics for the past week, but users can specify custom start and end dates to retrieve data for any time range. Additionally, users can filter the data based on specific criteria such as threatening or hateful tweets.

    Parameters:
    - start_date (optional): Start date of the time interval. If not provided, the default is set to one week before the end date.
    - end_date (optional): End date of the time interval. If not provided, the default is set to the current date.
    - page: Page number for pagination. Defaults to 1.
    - page_size: Number of results per page. Must be between 1 and 100. Defaults to 10.
    - criteria (optional): Criteria for filtering tweets. Can be 'threatening', 'hateful', or None.

    Example Date Format: "2023-09-05 14:04:15"

    Response:
    - A list of dictionaries containing the date and tweet count for each day within the specified time interval.
    """
    # Default end date is today
    if not end_date:
        end_date = datetime.now().date()
    # Default start date is last week
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # NOTE: these filters could be moved out.
    # They're used in data_filtering as well.
    threatening_filter = or_(
        Tweet.threat_level == "Medium",
        Tweet.threat_level == "High",
    )
    hateful_filter = or_(
        Tweet.hateful == "Medium",
        Tweet.hateful == "High",
    )
    offset = (page - 1) * page_size

    # Define the SQLAlchemy query
    query = (
        db.query(
            func.date(Tweet.created_at).label("date"),
            func.count().label("tweet_count"),
        )
        .filter(Tweet.created_at >= start_date, Tweet.created_at <= end_date)
        .group_by(func.date(Tweet.created_at))
        .order_by(func.date(Tweet.created_at))
        .limit(page_size)
        .offset(offset)
    )
    if criteria:
        if criteria == THREATENING:
            query.filter(threatening_filter)
        elif criteria == HATEFUL:
            query.filter(hateful_filter)
        else:
            raise NotImplementedError

    # Execute the query and convert results to a list of dictionaries
    result = [{"date": row.date, "tweet_count": row.tweet_count} for row in query]
    return result
