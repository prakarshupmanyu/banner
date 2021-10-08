FROM python:3.7-alpine

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

CMD sleep 60 \
&& python3 /app/stress_test.py
&& gunicorn -w 4 -b 0.0.0.0:8000 main:app