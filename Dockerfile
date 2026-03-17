FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt ./
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements-dev.txt

COPY . .

RUN python3 -m pip install -e ".[all]"

CMD ["geo2dcat", "formats"]
