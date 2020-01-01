FROM python:3.8.0-alpine3.10
MAINTAINER Harmon Hering <harmonherring@gmail.com>

RUN apk update && \
    apk add postgresql-dev gcc libffi-dev musl-dev

RUN mkdir /opt/masa-api

WORKDIR /opt/masa-api

COPY requirements.txt /opt/masa-api

RUN pip install -r requirements.txt

COPY . /opt/masa-api

ENV SQLALCHEMY_DATABASE_URI=None

CMD ["gunicorn", "app:app", "--bind=0.0.0.0:8081", "--workers=1"]
