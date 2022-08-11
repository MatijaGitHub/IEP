FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY ./auth.py ./auth.py
COPY ./adminDecorator.py ./adminDecorator.py
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./migrate.py ./migrate.py
COPY ./entry.sh ./entry.sh

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["./entry.sh"]
