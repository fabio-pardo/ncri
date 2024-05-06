# Use the official Python image as a base
FROM python:3.9-slim


# Set the working directory in the container
WORKDIR /code

# Copy the local code to the container
COPY requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
