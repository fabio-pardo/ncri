from datetime import datetime
from typing import Optional

from app.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.tweets import Tweet

visualization_data = APIRouter(
    prefix="/visualization_data",
    responses={
        404: {"description": "Not found"},
    },
)


@visualization_data.get("/twitter/trends")
@limiter.limit("5/minute")
def get_tweet_trends(
    request: Request,
    metric: str = Query(..., description="The metric to analyze (e.g., author)"),
    time_interval: str = Query(..., description="The time interval (e.g., day, month)"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves trends data from the tweets database table based on the specified parameters. It allows users to analyze trends over time for a given metric, such as the number of retweets, replies, or mentions, within a specified time interval (e.g., day, month). Pagination is supported to facilitate browsing through large result sets.

    Parameters:
    - metric: The metric to analyze, which corresponds to a column in the tweets table (e.g., "retweet_count", "author").
    - time_interval: The time interval to aggregate the data by (e.g., "day", "month").
    - start_date (optional): The start date for the analysis period.
    - end_date (optional): The end date for the analysis period.
    - page (optional): The page number for pagination (default is 1).
    - page_size (optional): The number of results per page (default is 10, maximum is 100).

    Response:
    - total_results: The total number of results available for the specified parameters.
    - page: The current page number.
    - page_size: The number of results per page.
    - data: An array containing the paginated results, each item containing the date, the value of the metric, and the count.
    """
    # Ensure the requested metric is a valid column in the Tweet model
    if not hasattr(Tweet, metric):
        raise HTTPException(status_code=400, detail="Invalid metric")

    # Calculate offset based on page number and page size
    offset = (page - 1) * page_size

    # Construct the query based on parameters
    query = db.query(
        func.date_trunc(time_interval, Tweet.datetime).label("date"),
        getattr(Tweet, metric).label("value"),
        func.count().label("count"),
    )

    if start_date:
        query = query.filter(Tweet.datetime >= start_date)
    if end_date:
        query = query.filter(Tweet.datetime <= end_date)

    query = query.group_by("date", "value").order_by("date")

    # Paginate the results
    total_results = query.count()
    results = query.offset(offset).limit(page_size).all()

    # Return paginated results
    return {
        "total_results": total_results,
        "page": page,
        "page_size": page_size,
        "data": [
            {"date": row.date, "value": row.value, "count": row.count}
            for row in results
        ],
    }


@visualization_data.get("/twitter/distribution")
@limiter.limit("5/minute")
def get_tweet_distribution(
    request: Request,
    metric: str = Query(
        ..., description="The metric to analyze (e.g., follower_count)"
    ),
    category: str = Query(
        ..., description="The category to group by (e.g., author, lang)"
    ),
    top_n: Optional[int] = Query(None, description="Limit the number of results"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves distribution data from the Twitter dataset based on the specified parameters. It allows users to analyze the distribution of a given metric across different categories, such as authors or languages, within the dataset. Pagination is supported to facilitate browsing through large result sets.

    Parameters:
    - metric: The metric to analyze, corresponding to a column in the Twitter dataset (e.g., "follower_count", "retweet_count").
    - category: The category to group the distribution by (e.g., "author", "lang").
    - top_n (optional): Limit the number of results returned.
    - page (optional): The page number for pagination (default is 1).
    - page_size (optional): The number of results per page (default is 10, maximum is 100).

    Response:
    - total_results: The total number of results available for the specified parameters.
    - page: The current page number.
    - page_size: The number of results per page.
    - data: An array containing the paginated results, each item containing the category value and the count of occurrences for the specified metric.
    """

    # Ensure the requested metric is a valid column in the Tweet model
    if not hasattr(Tweet, metric):
        raise HTTPException(status_code=400, detail="Invalid metric")

    # Ensure the requested category is a valid column in the Tweet model
    if not hasattr(Tweet, category):
        raise HTTPException(status_code=400, detail="Invalid category")

    # Calculate offset based on page number and page size
    offset = (page - 1) * page_size

    # Construct the query based on parameters
    try:
        query = db.query(getattr(Tweet, category), func.count().label("value"))
        query = query.group_by(getattr(Tweet, category)).order_by(func.count().desc())

        if top_n:
            query = query.limit(top_n)

        # Paginate the results
        total_results = query.count()
        results = query.offset(offset).limit(page_size).all()

        # Return paginated results
        return {
            "total_results": total_results,
            "page": page,
            "page_size": page_size,
            "data": [{"category": row[0], "value": row[1]} for row in results],
        }
    except InvalidRequestError as e:
        raise HTTPException(status_code=500, detail="Invalid request: " + str(e))


@visualization_data.get("/twitter/heatmap")
@limiter.limit("5/minute")
def get_tweet_heatmap(
    request: Request,
    start_date: datetime = Query(..., description="Start date of the date range"),
    end_date: datetime = Query(..., description="End date of the date range"),
    threat_level: str = Query(
        None, description="Threat level to filter tweets (optional)"
    ),
    db: Session = Depends(get_db),
):
    """
    Description: This endpoint retrieves heatmap data for tweets based on the specified date range. It allows users to analyze tweet activity over time and visualize trends. Optionally, users can filter tweets by threat level to focus on specific types of tweets.

    Parameters:
    - start_date: Start date of the date range.
    - end_date: End date of the date range.
    - threat_level (optional): Threat level to filter tweets.

    Response:
    - A 2D list representing the heatmap data, where each row corresponds to a month and each column corresponds to a day. The value at each cell represents the count of tweets for that day.
    """

    # Query the database for tweet counts per day
    query = db.query(Tweet.year, Tweet.month, Tweet.day)

    if threat_level:
        query = query.filter(Tweet.threat_level == threat_level)

    tweet_counts = (
        query.filter(Tweet.datetime >= start_date, Tweet.datetime <= end_date)
        .group_by(Tweet.year, Tweet.month, Tweet.day)
        .order_by(Tweet.year, Tweet.month, Tweet.day)
        .all()
    )

    # Create a 2D list to store heatmap data
    heatmap_data = [
        [0 for _ in range(31)] for _ in range(12)
    ]  # Assuming maximum 12 months and 31 days

    # Populate the heatmap data based on query results
    for _, month, day in tweet_counts:
        heatmap_data[month - 1][day - 1] += 1  # Adjust month and day indices

    return heatmap_data
