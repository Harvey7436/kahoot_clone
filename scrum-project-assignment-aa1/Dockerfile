FROM python:slim

RUN useradd trivia

WORKDIR /home/trivia

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY trivia.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP trivia.py

RUN chown -R trivia:trivia ./
USER trivia

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]