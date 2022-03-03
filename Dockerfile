FROM python:3.10-bullseye

WORKDIR /app
COPY . ./

RUN mkdir -p bin
RUN wget -nc -P /app/bin https://github.com/Backblaze/B2_Command_Line_Tool/releases/latest/download/b2-linux

RUN mkdir -p config
RUN mv config.json /app/config

ENTRYPOINT [ "python3", "main.py" ]