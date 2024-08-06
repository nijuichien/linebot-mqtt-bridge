FROM python:3.11.10-slim-bullseye

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt