FROM python:3.10-slim

WORKDIR /app

COPY dbtest.py .


RUN pip install psycopg2-binary


CMD [ "python", "dbtest.py" ]