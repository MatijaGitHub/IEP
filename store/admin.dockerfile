FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY ./admin.py ./admin.py
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./migrate.py ./migrate.py
COPY ./adminDecorator.py ./adminDecorator.py
COPY ./entry.sh ./entry.sh

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"

ENTRYPOINT ["./entry.sh"]