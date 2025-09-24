FROM python:3.13.7-alpine3.22

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /opt

ENTRYPOINT FLASK_APP=/opt/app.py flask run --host=0.0.0.0
