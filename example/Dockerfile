FROM cgialus/alus-runtime:latest

RUN mkdir /app
WORKDIR /app

ADD https://github.com/cgi-estonia-space/ALUs/releases/download/v1.5.0/alus-1-5-0.zip .
RUN unzip alus-1-5-0.zip
RUN mv alus-1-5-0/* .
RUN chmod +x alus-coh
ENV PATH="$PATH:/app"

COPY requirements.txt .
COPY processor.py .
COPY data_prepare.py .
COPY structlog_cloudferro.py .
COPY demloader_get_from_aoi.py .
RUN apt update && apt install -y python3-pip
RUN pip install -r requirements.txt
