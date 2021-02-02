FROM python:3.7-alpine
MAINTAINER Tre W Developments

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /neuro_app
WORKDIR /neuro_app
COPY . /neuro_app
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--insecure"]
