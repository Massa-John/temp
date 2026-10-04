# temp

Публичный сайт для загрузки роликов с YouTube в **одном Docker-контейнере**.

## Возможности
- Загрузка по URL YouTube
- Выбор качества:
  - `best`
  - `720p`
  - `audio only`
- Базовая валидация YouTube URL
- Ограничение максимального размера файла (`MAX_SIZE_MB`)
- Слушает трафик на порту **9090**

## Быстрый запуск (Docker)
```bash
docker build -t temp .
docker run --rm -p 9090:9090 \
  -e MAX_SIZE_MB=500 \
  -e SECRET_KEY=change-me \
  -v temp_downloads:/app/downloads \
  temp
```

Откройте: http://localhost:9090

## Запуск через docker-compose
```bash
docker compose up --build
```

## Переменные окружения
- `MAX_SIZE_MB` — лимит размера файла в MB (по умолчанию: `500`)
- `SECRET_KEY` — ключ Flask сессий
- `DOWNLOAD_DIR` — директория для загрузок внутри контейнера (по умолчанию: `/app/downloads`)

## Важно
Используйте только в рамках законодательства и правил платформы, а также с соблюдением авторских прав.
