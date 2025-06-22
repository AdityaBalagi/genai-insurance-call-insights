FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r app/requirements.txt


CMD ["python3", "app/main.py"]
