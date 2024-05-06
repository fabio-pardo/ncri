from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

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
async def get_key_user_stats(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    """Returns all users and the count of their tweets in descending order."""
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
async def get_specific_tweet_stats(
    start_date: Optional[datetime] = Query(default=None, description="Start date"),
    end_date: Optional[datetime] = Query(default=None, description="End date"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    criteria: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve twitter data based on set time interval.
    Default time interval is set to the past week.
    One may also pass in the criteria they want to search on.
    Criteria may be `threatening`, `hateful` or `None`
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
