FROM cgialus/alus-devel:latest

RUN mkdir /app
WORKDIR /app
COPY requirements.txt .

COPY processor.py .
RUN pip install -r requirements.txt
