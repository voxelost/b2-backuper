FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . ./

RUN mkdir -p config
RUN mv config.json /app/config

RUN pip install b2sdk

ENTRYPOINT [ "python3", "main.py" ]