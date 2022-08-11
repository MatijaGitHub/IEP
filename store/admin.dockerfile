FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY ./admin.py ./admin.py
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./migrate.py ./migrate.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"

ENTRYPOINT ["python","admin.py"]