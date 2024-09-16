# docker build -t manga .
# docker run manga 

FROM python:3.8-slim-bullseye


WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app

RUN apt-get update \
    && apt-get -y --no-install-recommends install gcc libxml2-dev libxslt-dev python3-dev python3-lxml \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r dev-requirements.txt

# ENTRYPOINT ["python3", "scraper/"]
