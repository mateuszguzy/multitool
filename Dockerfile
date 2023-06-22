FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY ./requirements/dev.txt /app/
WORKDIR /app
RUN pip install -r dev.txt
COPY . /app/
