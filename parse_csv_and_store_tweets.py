import csv

from sqlalchemy.dialects.postgresql import insert

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

nullable_boolean_keys = ["retweeted", "len_filter"]
tweets = read_csv(file_path, data_dict)

# Hacky way to get around None valued string to be bool or Nonetype.
# Could be better I know, but in the purpose of saving time.
for tweet in tweets:
    for key in nullable_boolean_keys:
        value = tweet[key]
        if value == "False":
            tweet[key] = False
        elif value == "True":
            tweet[key] = True
        else:
            tweet[key] = None

# Do nothing because we see conflicts of duplicate tweets due to
# inserting same pkey multiple times.
insert_stmt = insert(Tweet).values(tweets).on_conflict_do_nothing()
with SessionLocal() as session:
    session.execute(insert_stmt)
    session.commit()
