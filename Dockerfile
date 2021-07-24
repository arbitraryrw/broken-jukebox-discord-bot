 # syntax=docker/dockerfile:1
FROM python:3.8-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "run.py"]