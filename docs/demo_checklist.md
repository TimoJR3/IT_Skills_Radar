# Demo checklist

## Перед показом

- Убедиться, что Docker Desktop запущен.
- Выполнить `docker compose up --build -d`.
- Подготовить демо-данные: `docker compose exec api python -m app.db.prepare_demo`.
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
- Показать верхнюю командную панель radar-интерфейса и data flow: `JSON/CSV -> валидация -> нормализация -> PostgreSQL -> SQL-витрины -> FastAPI -> Streamlit`.

## Сценарий demo

1. Открыть dashboard.
2. Показать горизонтальную панель фильтров без sidebar: роль, уровень, навыки, период.
3. Выбрать `Data Scientist` и `junior`.
4. Открыть вкладку `Карта рынка`: профиль роли, skill tiles, skill chips и интерпретация.
5. Открыть вкладку `Матрица навыков` и показать heatmap-style сравнение навыков.
6. Открыть вкладку `Динамика спроса` и показать `Python` или `SQL`.
7. Открыть вкладку `Зарплатный сигнал`.
8. Открыть вкладку `Junior / Intern`.
9. Открыть вкладку `Проверка демо` и показать, что API, БД, SQL-витрины и демо-данные доступны.
10. При желании открыть Swagger и показать API endpoints.

## Ключевые тезисы во время demo

- Метрики считаются заранее в PostgreSQL views.
- FastAPI не пересчитывает аналитику на лету, а отдает готовые агрегаты.
- Streamlit работает как thin UI поверх API.
- Raw payload хранится отдельно от final слоя.
- Если endpoint или БД недоступны, dashboard показывает понятную диагностику вместо traceback.
- Интерфейс сделан как `Radar Workspace`: вкладки, карта рынка, матрица навыков и skill chips вместо классического BI-dashboard.

## Если `/roles` возвращает ошибку

- Проверить `docker compose ps`.
- Проверить `http://localhost:8000/health`.
- Проверить `http://localhost:8000/roles`.
- Повторно выполнить `make init-db`, `make init-analytics`, `make seed-db`.
- Открыть Swagger: `http://localhost:8000/docs`.

## Что сказать в конце

- Проект демонстрирует полный путь данных: ingestion -> normalization -> storage -> analytics -> API -> UI.
- Архитектура специально сделана простой, чтобы ее можно было быстро объяснить и легко поддерживать.
- Следующий шаг — подключение реальных источников вакансий и расширение аналитики.
