FROM cgialus/alus-runtime:latest

RUN mkdir /app
WORKDIR /app

ADD https://github.com/cgi-estonia-space/ALUs/releases/download/v1.4.0/alus-1-4-0.tar.gz .
RUN tar -xzvf alus-1-4-0.tar.gz
RUN chmod +x alus-coh
ENV PATH="$PATH:/app"

COPY requirements.txt .
COPY processor.py .
COPY demloader_get_from_aoi.py .
RUN apt update && apt install -y python3-pip
RUN pip install -r requirements.txt
