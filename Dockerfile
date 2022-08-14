FROM python:3.10.4-buster
LABEL Maintainer="Edition-X"
RUN mkdir -p /usr/app/src/logs
WORKDIR /usr/app/src
COPY *.py config.json requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
CMD ["python", "./main.py"]
