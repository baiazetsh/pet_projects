#!/bin/sh
set -e

echo "[INIT] Запуск ollama serve..."
ollama serve &

sleep 5

echo "[INIT] Проверяю модель: $OLLAMA_MODEL"
if ! ollama list | grep -q "$OLLAMA_MODEL"; then
  echo "[INIT] Модель $OLLAMA_MODEL не найдена — качаю..."
  ollama pull "$OLLAMA_MODEL"
else
  echo "[INIT] Модель $OLLAMA_MODEL уже есть."
fi

echo "[INIT] Контейнер готов, держим процесс живым"
tail -f /dev/null
