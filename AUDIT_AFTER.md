# Audit After

## Найденные проблемы

- В корне репозитория лежал служебный файл `.Rhistory`.
- В корне лежали скриншоты с техническими именами `photo_2026-04-30_*.jpg`.
- Скриншоты были продублированы в `docs/assets`, а README ссылался на старый каталог.
- README недостаточно явно объяснял проект как portfolio data-project для аналитической стажировки.
- В README не хватало executive summary, роли автора как аналитика, grain/полей/бизнес-вопросов по витринам и подробных ограничений интерпретации.
- Не было отдельного документа для защиты проекта на интервью.

## Исправления

- Удален `.Rhistory`; правило `.Rhistory` уже присутствует в `.gitignore`.
- Скриншоты перенесены в `docs/images/` с осмысленными именами:
  - `dashboard_market_overview.jpg`
  - `dashboard_top_skills.jpg`
  - `swagger_api.jpg`
- Удалены дублирующие изображения из `docs/assets`.
- README переписан как GitHub-портфолио: добавлены executive summary, аналитический вклад, подписи к скриншотам, SQL-витрины, dashboard storytelling и ограничения.
- Усилен `docs/analytics.md`: для витрин добавлены grain, поля, бизнес-вопросы и ограничения интерпретации.
- Добавлен `docs/interview_defense.md` с 60-секундным объяснением, вопросами и честными ответами про ограничения данных.

## Измененные файлы

- `.Rhistory` удален
- `README.md`
- `docs/analytics.md`
- `docs/interview_defense.md`
- `docs/images/dashboard_market_overview.jpg`
- `docs/images/dashboard_top_skills.jpg`
- `docs/images/swagger_api.jpg`
- `docs/assets/dashboard-market-map.jpg` удален
- `docs/assets/dashboard-top-skills-chart.jpg` удален
- `docs/assets/swagger-api-docs.jpg` удален
- `photo_2026-04-30_01-46-43.jpg` удален
- `photo_2026-04-30_01-46-57.jpg` удален
- `photo_2026-04-30_01-47-24.jpg` удален

## Команды проверки

```bash
python -m pytest -q
python -m compileall app dashboard tests
cp .env.example .env
docker compose config
docker compose up --build -d
python -m uvicorn app.main:app --host 127.0.0.1 --port 18000
curl -I http://127.0.0.1:18000/docs
curl http://127.0.0.1:18000/health
curl http://127.0.0.1:18000/openapi.json
API_URL=http://127.0.0.1:18000 python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 18501 --server.headless true
curl -I http://127.0.0.1:18501
command -v gh && gh run list --limit 5
```

## Результаты проверки

- `python -m pytest -q`: успешно, `48 passed`, есть только deprecation warnings из внешних зависимостей окружения.
- `python -m compileall app dashboard tests`: успешно.
- `docker compose config`: успешно после временного создания `.env` из `.env.example`; compose-файл валиден.
- `docker compose up --build -d`: не выполнен полностью, потому что Docker daemon недоступен: `Cannot connect to the Docker daemon at unix:///Users/timurgasanov/.docker/run/docker.sock`.
- FastAPI Swagger: локально проверен без Docker через `python -m uvicorn ... --port 18000`; `GET /docs` вернул `200 OK`.
- FastAPI health: `GET /health` вернул `{"status":"ok"}`.
- FastAPI OpenAPI: в схеме присутствуют `/health`, `/roles`, `/skills/top`, `/skills/trends`, `/salary/premium`, `/overview/junior`.
- Streamlit dashboard: локально запущен на `http://127.0.0.1:18501`, HTTP-проверка вернула `200 OK`.
- Полная проверка dashboard с данными через PostgreSQL не выполнена, потому что PostgreSQL должен подниматься через Docker Compose, а Docker daemon в текущей среде недоступен.
- Browser visual snapshot через Playwright не выполнен: пакет Playwright доступен, но браузерный binary отсутствует; `npx` не установлен, `python -m playwright` тоже недоступен.
- GitHub Actions: локально повторены команды из `.github/workflows/ci.yml` (`compileall` и `pytest -q`), они прошли успешно. Удаленные run-ы не проверены, потому что `gh` не установлен в текущем окружении; фактический статус GitHub Actions подтвердится после push/PR.

## Финальный pre-commit git status

```text
 D .Rhistory
 M README.md
 M docs/analytics.md
 D docs/assets/dashboard-market-map.jpg
 D docs/assets/dashboard-top-skills-chart.jpg
 D docs/assets/swagger-api-docs.jpg
 M docs/resume_bullets.md
 D photo_2026-04-30_01-46-43.jpg
 D photo_2026-04-30_01-46-57.jpg
 D photo_2026-04-30_01-47-24.jpg
?? AUDIT_AFTER.md
?? docs/images/
?? docs/interview_defense.md
```

В коммит должны попасть только ожидаемые portfolio-polish изменения: удаление служебных/случайных артефактов, перенос скриншотов, README и docs.

## Оставшиеся риски

- Данные подготовлены локально и не являются полной репрезентативной выгрузкой вакансий.
- Salary premium остается аналитическим сигналом, а не причинным выводом.
- При малом числе вакансий медианы и доли могут быть нестабильны.
- Rule-based normalization skills может ошибаться на новых формулировках.
- Без push/PR нельзя подтвердить фактический удаленный статус GitHub Actions, можно только проверить совпадение локальных команд с CI workflow.
- Docker-based запуск нужно повторить после старта Docker Desktop.
- Просмотр удаленных GitHub Actions run-ов нужно повторить в окружении с установленным `gh` или через GitHub UI.
