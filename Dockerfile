FROM python:3.10.4-buster
LABEL Maintainer="Edition-X"
RUN mkdir -p /usr/app/src/logs
WORKDIR /usr/app/src
COPY *.py requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN opentelemetry-bootstrap --action=install
CMD ["opentelemetry-instrument", "python", "./main.py"]
