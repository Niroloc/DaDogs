FROM python:3.10.18@sha256:4585309097d523698d382a2de388340896e021319b327e2d9c028f3b4c316138
USER root
WORKDIR /app

COPY requirements.txt
RUN pip3 install -r requirements.txt

ADD src .

CMD ["python3", "-u", "run_bot.py"]