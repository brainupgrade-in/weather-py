FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache py3-pip
RUN pip install -r requirements.txt

COPY app.py ./
RUN apk del py3-pip
RUN rm -rf /var/lib/apk/cache

ENV API_URL_GEOCODING https://geocoding-api.open-meteo.com/v1
ENV API_URL_WEATHER https://api.open-meteo.com/v1
ENV ENVIRONMENT uat

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

# docker build -t brainupgrade/configmap:2 .
# docker run -p 8080:8080 brainupgrade/configmap:2
# docker build -t brainupgrade/weathe-py:2 -t brainupgrade/weathe-py:latest .