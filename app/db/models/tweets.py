from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.database import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)

    author = Column(String, index=True)
    author_created_utc = Column(DateTime)
    clean_text = Column(String)
    created_at = Column(DateTime, index=True)
    datetime = Column(DateTime, index=True)
    day = Column(Integer, index=True)
    follower_count = Column(Integer)
    full_text = Column(String)
    hateful = Column(Boolean, default=False, index=True)
    lang = Column(String, index=True)
    len_filter = Column(Boolean, default=False, index=True)
    minute = Column(Integer, index=True)
    month = Column(Integer, index=True)
    reply_count = Column(Integer)
    retweet_count = Column(Integer)
    retweeted = Column(Boolean)
    second = Column(Integer)
    text = Column(String)
    threat_level = Column(String, index=True)
    year = Column(Integer, index=True)
    year_month = Column(String, index=True)
    year_month_day = Column(String, index=True)
    zip = Column(Integer, index=True)
