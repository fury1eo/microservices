FROM python:3.10.9-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc

COPY requirements.ms ./

RUN pip3 install -r requirements.ms

COPY . .

CMD ["python3", "main.py"]