#Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# web будет запускать python manage.py runserver
# celery будет запускать celery -A blg worker ...
