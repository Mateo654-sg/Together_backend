# 🚀 Together

# Documento 08 — Backend API Specification

**Versión:** 1.0

**Estado:** Aprobado

**Framework:** FastAPI

**Lenguaje:** Python 3.12+

**Arquitectura:** Clean Architecture

**Estilo:** RESTful API

---

# Objetivo

Este documento define la especificación completa de la API REST de Together.

Todos los servicios deberán seguir este estándar.

La API será:

- RESTful
- Stateless
- Versionada
- Documentada con OpenAPI
- Segura mediante JWT
- Escalable
- Fácil de mantener

---

# Base URL

## Desarrollo

```
http://localhost:8000/api/v1
```

## Producción

```
https://api.together.app/api/v1
```

---

# Versionado

Toda la API utilizará versionado.

```
/api/v1
```

Las futuras versiones deberán mantener compatibilidad hacia atrás siempre que sea posible.

---

# Formato

Todos los endpoints consumirán y devolverán JSON.

Ejemplo

```json
{
  "success": true,
  "message": "Expense created successfully.",
  "data": {}
}
```

---

# Códigos HTTP

| Código | Descripción |
|---------|-------------|
|200|OK|
|201|Created|
|204|No Content|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|429|Too Many Requests|
|500|Internal Server Error|

---

# Headers

Authorization

```
Bearer JWT_TOKEN
```

Content-Type

```
application/json
```

Accept

```
application/json
```

---

# Respuesta Exitosa

```json
{
    "success": true,
    "message": "Request successful",
    "data": {}
}
```

---

# Respuesta Error

```json
{
    "success": false,
    "message": "Expense not found.",
    "errors": []
}
```

---

# PAGINACIÓN

Formato

```
?page=1&limit=20
```

Respuesta

```json
{
  "data": [],
  "pagination": {
      "page":1,
      "limit":20,
      "total":320,
      "pages":16
  }
}
```

---

# FILTROS

Ejemplo

```
GET /expenses?category=food
```

```
GET /expenses?year=2026
```

```
GET /expenses?month=6
```

```
GET /expenses?min=10000
```

```
GET /expenses?max=500000
```

---

# ORDENAMIENTO

```
sort=created_at

sort=amount

sort=name
```

---

# AUTH

---

## POST

/auth/register

Crear usuario.

---

Body

```json
{
    "first_name":"Mateo",
    "last_name":"Rico",
    "email":"mail@email.com",
    "password":"********"
}
```

---

Respuesta

201

---

## POST

/auth/login

---

```json
{
    "email":"",
    "password":""
}
```

---

Respuesta

```json
{
    "access_token":"",
    "refresh_token":""
}
```

---

## POST

/auth/refresh

---

## POST

/auth/logout

---

## POST

/auth/forgot-password

---

## POST

/auth/reset-password

---

## POST

/verify-email

---

# USERS

---

GET

/users/me

---

PUT

/users/me

---

DELETE

/users/me

---

PATCH

/users/avatar

---

GET

/users/statistics

---

GET

/users/settings

---

PUT

/users/settings

---

# COUPLES

---

POST

/couples/invite

---

POST

/couples/accept

---

POST

/couples/reject

---

DELETE

/couples/unlink

---

GET

/couples

---

GET

/couples/dashboard

---

GET

/couples/statistics

---

# PERSONAL EXPENSES

---

GET

/expenses

---

GET

/expenses/{id}

---

POST

/expenses

---

PUT

/expenses/{id}

---

DELETE

/expenses/{id}

---

POST

/expenses/duplicate

---

POST

/expenses/upload-receipt

---

GET

/expenses/search

---

GET

/expenses/filter

---

GET

/expenses/export

---

# PERSONAL INCOMES

---

GET

/incomes

---

POST

/incomes

---

PUT

/incomes/{id}

---

DELETE

/incomes/{id}

---

# SHARED EXPENSES

---

GET

/shared-expenses

---

POST

/shared-expenses

---

PUT

/shared-expenses/{id}

---

DELETE

/shared-expenses/{id}

---

POST

/shared-expenses/split

---

POST

/shared-expenses/pay

---

GET

/shared-expenses/history

---

# DEBTS

---

GET

/debts

---

POST

/debts/pay

---

PATCH

/debts/{id}

---

GET

/debts/history

---

# GOALS

---

GET

/goals

---

POST

/goals

---

PUT

/goals/{id}

---

DELETE

/goals/{id}

---

POST

/goals/contribute

---

GET

/goals/history

---

GET

/goals/statistics

---

# BUDGETS

---

GET

/budgets

---

POST

/budgets

---

PUT

/budgets/{id}

---

DELETE

/budgets/{id}

---

GET

/budgets/alerts

---

# REMINDERS

---

GET

/reminders

---

POST

/reminders

---

PUT

/reminders/{id}

---

DELETE

/reminders/{id}

---

PATCH

/reminders/{id}/complete

---

# REPORTS

---

GET

/reports

---

POST

/reports/generate

---

GET

/reports/download/{id}

---

DELETE

/reports/{id}

---

# NOTIFICATIONS

---

GET

/notifications

---

PATCH

/notifications/read

---

PATCH

/notifications/read-all

---

DELETE

/notifications/{id}

---

# CHAT

---

GET

/chat

---

POST

/chat

---

DELETE

/chat/{id}

---

POST

/chat/upload

---

# AI

---

POST

/ai/chat

---

POST

/ai/analyze

---

POST

/ai/predictions

---

GET

/ai/history

---

DELETE

/ai/history

---

GET

/ai/insights

---

POST

/ai/score

---

POST

/ai/recommendations

---

POST

/ai/monthly-summary

---

POST

/ai/weekly-summary

---

POST

/ai/financial-health

---

POST

/ai/simulate

---

Ejemplo

```json
{
   "question":"¿Cuánto gastamos este año en restaurantes?"
}
```

---

Respuesta

```json
{
    "answer":"Durante este año han gastado $4.320.000 en restaurantes..."
}
```

---

# FILES

---

POST

/files

---

DELETE

/files/{id}

---

GET

/files/{id}

---

# EXPORTS

---

POST

/exports/pdf

---

POST

/exports/excel

---

POST

/exports/csv

---

# SEARCH

---

GET

/search

Buscar:

- gastos

- ingresos

- metas

- categorías

- recordatorios

---

# DASHBOARD

---

GET

/dashboard

---

Respuesta

```json
{
    "balance":0,
    "income":0,
    "expense":0,
    "saving":0,
    "goals":[],
    "statistics":{}
}
```

---

# KPIs

---

GET

/statistics/month

---

GET

/statistics/year

---

GET

/statistics/category

---

GET

/statistics/couple

---

GET

/statistics/personal

---

# ADMIN (Futuro)

---

GET

/admin/users

---

GET

/admin/statistics

---

GET

/admin/errors

---

GET

/admin/logs

---

GET

/admin/health

---

# Rate Limiting

Endpoints públicos

100 requests/min

Endpoints autenticados

500 requests/min

AI

20 requests/min

Login

5 intentos/min

---

# Seguridad

JWT

Refresh Token

HTTPS

CORS

Rate Limiting

Argon2

AES

Validación Pydantic

Sanitización de entradas

---

# Validaciones

Todos los datos recibidos deberán validarse mediante Pydantic.

Ejemplos

- Email válido.
- Contraseña segura.
- UUID válido.
- Fechas válidas.
- Montos positivos.
- Longitud máxima de cadenas.
- Archivos permitidos (MIME y tamaño).

---

# Documentación

La API deberá generar automáticamente:

- Swagger UI (`/docs`)
- ReDoc (`/redoc`)
- OpenAPI 3.1

---

# Logging

Registrar:

- Requests
- Errores
- Latencia
- Usuario autenticado
- Endpoint consumido
- Código de respuesta

---

# Testing

Cada endpoint deberá contar con:

- Pruebas unitarias.
- Pruebas de integración.
- Casos de éxito.
- Casos de error.
- Validaciones de permisos.

Cobertura mínima del backend: **90%**.

---

# Convenciones

## Endpoints

Plural

Ejemplo

```
/expenses
/goals
/users
```

---

## Recursos

Siempre usar sustantivos.

Incorrecto

```
/createExpense
```

Correcto

```
POST /expenses
```

---

# Principio Final

La API de Together deberá diseñarse bajo los principios de simplicidad, seguridad y escalabilidad.

Cada endpoint debe ser:

- Consistente.
- Versionado.
- Documentado.
- Tipado.
- Seguro.
- Fácil de consumir desde Flutter u otros clientes.

Esta especificación constituye el contrato oficial entre el frontend y el backend y servirá como base para la implementación con FastAPI.