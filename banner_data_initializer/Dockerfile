# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

COPY . .

RUN pip install --trusted-host pypi.org --user -r requirements.txt

RUN apt-get update -y \
    && apt-get install openjdk-11-jdk -y \
    && apt-get install wget -y

RUN wget https://downloads.apache.org/spark/spark-3.0.3/spark-3.0.3-bin-hadoop2.7.tgz \
    && tar xvf spark-* \
    && mv spark-3.0.3-bin-hadoop2.7 /opt/spark

COPY lib/mysql-connector-java-8.0.26.jar /opt/spark/jars/

ENV SPARK_HOME="/opt/spark"

CMD sleep 30 \
&& /opt/spark/bin/spark-submit /app/banner_data_processor.py