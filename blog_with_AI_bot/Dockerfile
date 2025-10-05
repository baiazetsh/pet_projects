# Dockerfile

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y curl gnupg build-essential

# Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs





# Copy Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Копируем аватарки в контейнер
RUN mkdir -p /app/media/avatars
COPY media/avatars/ /app/media/avatars/

# Собираем статику
RUN python manage.py collectstatic --noinput || true

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "blg.asgi:application"]

# UnoCSS build


