FROM python:3.11-slim

WORKDIR /app

COPY main.py .
COPY models.py .
COPY __init__.py .

RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
