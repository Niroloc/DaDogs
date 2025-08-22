FROM ubuntu:latest
LABEL authors="cicn"

ENTRYPOINT ["top", "-b"]