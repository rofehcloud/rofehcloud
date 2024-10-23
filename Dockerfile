FROM python:3.13.0-slim-bookworm

RUN apt-get update && apt-get upgrade -y --no-install-recommends

RUN apt install --no-install-recommends -y curl

RUN groupadd -g 1000 appuser && useradd -u 1000 -m -g appuser appuser

WORKDIR /app

ARG TARGETARCH

# Installing dependencies 
RUN pip3 install --no-cache-dir -r requirements.txt

COPY main.py /app/main.py
COPY common /app/common


ENV PYTHONPATH=/app:/app/common

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]