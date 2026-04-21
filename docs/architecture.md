# Architecture Overview

## Goal

The project is intentionally simple: a small backend, a lightweight dashboard, and a PostgreSQL database. This keeps the code readable and realistic for a junior portfolio project while still showing good engineering structure.

## Layered Structure

```text
Streamlit dashboard
        |
        v
FastAPI API layer
        |
        v
Service layer
        |
        v
DB access layer
        |
        v
PostgreSQL
```

## Responsibilities

### `app/api`
HTTP endpoints and request routing. Keeps web concerns separated from business logic.

### `app/services`
Application logic. In future stages this layer will orchestrate ingestion, normalization, and analytics.

### `app/db`
Database connection utilities and shared DB-related code.

### `app/models`
Database models for tables and persistence entities.

### `app/schemas`
Pydantic schemas for request and response validation.

### `app/core`
Core settings and shared configuration.

### `dashboard`
Streamlit user interface for quick analytics views and portfolio demo screens.

### `tests`
Basic automated tests for API and future service logic.

## Why This Structure

This scaffold demonstrates:
- clean separation of concerns
- API and UI packaged as separate services
- database-ready setup
- test-ready development workflow
- straightforward path for future extension without overengineering

