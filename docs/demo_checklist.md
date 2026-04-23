# Demo checklist

## Перед показом

- Убедиться, что Docker Desktop запущен.
- Выполнить `docker compose up --build -d`.
- Проверить `http://localhost:8000/health`.
- При необходимости повторно применить:
  - `make init-db`
  - `make init-analytics`
  - `make seed-db`
- При необходимости повторно прогнать ingestion:
  - `docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual`
  - `docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual`

## Что показать в начале

- Кратко объяснить идею: анализ спроса на навыки в data/product вакансиях.
- Показать, что проект не ограничивается ноутбуком: есть база, ingestion, API, dashboard, тесты и CI.

## Сценарий demo

1. Открыть dashboard.
2. Показать фильтры по роли и уровню.
3. Выбрать `Data Scientist` и `junior`.
4. Показать блок топ навыков.
5. Показать график динамики навыка `Python` или `SQL`.
6. Показать блок salary premium.
7. Показать junior / intern overview.
8. При желании открыть Swagger и показать API endpoints.

## Ключевые тезисы во время demo

- Метрики считаются заранее в PostgreSQL views.
- FastAPI не пересчитывает аналитику на лету, а отдает готовые агрегаты.
- Streamlit работает как thin UI поверх API.
- Raw payload хранится отдельно от final слоя.

## Что сказать в конце

- Проект демонстрирует полный путь данных: ingestion -> normalization -> storage -> analytics -> API -> UI.
- Архитектура специально сделана простой, чтобы ее можно было быстро объяснить и легко поддерживать.
- Следующий шаг — подключение реальных источников вакансий и расширение аналитики.
