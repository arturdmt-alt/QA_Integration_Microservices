FROM python:3.11-slim

WORKDIR /app

COPY app.py .
COPY __init__.py .

RUN pip install --no-cache-dir flask==3.0.0 requests==2.31.0

EXPOSE 8002

CMD ["python", "app.py"]
