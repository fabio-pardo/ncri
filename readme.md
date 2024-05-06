# NCRI

Getting started:
- Create a venv
- Using the python version 3.8.18
- I used something like the following: `mkvirtualenv -p ~/.pyenv/versions/3.8.18/bin/python3.8 ncri`
- Run `docker-compose up --build`
- Run `alembic upgrade head`
- Run `python parse_csv_and_store_tweets.py`
- The PostgreSQL DB and the NCRI web service should be up and running now.

To ensure that the webservice is up and running:
- Reach localhost:8000 for "Hello World"

To ensure that the tweets are in the DB run the following:
  - Make sure you have `psql` on your machine
  - If not, do `brew install postgresql` assuming you have `brew` on your machine.
  - Run `export PGPASSWORD="ncri"; psql -U ncri -d ncri -h localhost -p 5432` to enter the PG DB.
  - `select count(*) from tweets;` should return 40106 rows, meaning the DB is ready.
