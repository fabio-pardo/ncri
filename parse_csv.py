import csv

from app.db.database import SessionLocal
from app.db.models.tweets import Tweet

file_path = "./screener_tweets.csv"


def read_csv(filename, required_columns):
    data = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Filter out only the required columns
            filtered_row = {col: row[col] for col in required_columns}
            data.append(filtered_row)
    return data


data_dict = {
    "lang",
    "retweet_count",
    "retweeted",
    "created_at",
    "full_text",
    "reply_count",
    "id",
    "author",
    "author_created_utc",
    "text",
    "len_filter",
    "clean_text",
    "datetime",
    "year",
    "month",
    "day",
    "minute",
    "second",
    "year_month",
    "year_month_day",
    "follower_count",
    "threat_level",
    "hateful",
    "zip",
}

tweets = read_csv(file_path, data_dict)
session = SessionLocal()

session.bulk_insert_mappings(Tweet, tweets)

session.commit()

session.close()
