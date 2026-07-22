# 🏗️ Together

# Documento 06 — Arquitectura del Sistema

**Versión:** 1.0

**Estado:** Aprobado

---

# Objetivo

Este documento define la arquitectura técnica oficial de Together.

La arquitectura deberá ser:

- Escalable
- Modular
- Segura
- Fácil de mantener
- Cloud Ready
- Mobile First

El sistema debe soportar el crecimiento del producto desde un MVP para parejas hasta una plataforma financiera utilizada por cientos de miles de usuarios.

---

# Principios Arquitectónicos

Toda decisión técnica deberá cumplir los siguientes principios.

## Clean Architecture

Separación estricta entre:

- Presentation
- Application
- Domain
- Infrastructure

---

## SOLID

Todo módulo deberá seguir:

- Single Responsibility
- Open / Closed
- Liskov
- Interface Segregation
- Dependency Inversion

---

## DRY

Nunca duplicar lógica.

---

## KISS

Las soluciones simples siempre tendrán prioridad.

---

## Modularidad

Cada módulo debe ser independiente.

Ejemplo

Usuarios

no debe depender de

Metas

---

## Escalabilidad

Toda funcionalidad deberá permitir:

- Horizontal Scaling
- Vertical Scaling

---

# Arquitectura General

```text
                    Flutter App

                           │

                HTTPS REST API

                           │

                   FastAPI Backend

        ┌────────────┬────────────┬─────────────┐
        │            │            │
 Authentication   Business     AI Services
        │            │            │
        └────────────┴────────────┘
                     │
              PostgreSQL Database
                     │
       ┌─────────────┴─────────────┐
       │                           │
     Redis                     Firebase
(Cache / Sessions)         Push Notifications

                     │

             AWS Infrastructure
```

---

# Stack Tecnológico

## Frontend

Flutter

Material 3

Riverpod

GoRouter

Dio

Freezed

Json Serializable

Flutter Secure Storage

Hive

---

## Backend

FastAPI

SQLAlchemy 2

Alembic

Pydantic

JWT

OAuth2

Python 3.12+

---

## Base de Datos

PostgreSQL

UUID

JSONB

Indexes

Triggers

Views

Stored Procedures (solo cuando aporten valor)

---

## Cache

Redis

Usos

- Cache Dashboard
- Tokens
- IA
- Sesiones
- Rate Limiting

---

## Notificaciones

Firebase Cloud Messaging

---

## Infraestructura

Docker

Docker Compose

GitHub Actions

AWS

---

# Arquitectura Flutter

Se utilizará MVVM.

```text
lib/

core/

features/

shared/

routes/

theme/

services/
```

---

Cada Feature tendrá:

```text
feature/

data/

domain/

presentation/
```

---

Ejemplo

```text
expenses/

data/

repositories

datasources

models

domain/

entities

repositories

usecases

presentation/

pages

widgets

viewmodels
```

---

# Arquitectura Backend

```text
app/

api/

core/

db/

models/

schemas/

repositories/

services/

use_cases/

middlewares/

utils/

tests/
```

---

Cada módulo tendrá:

```text
users/

expenses/

goals/

budgets/

ai/

notifications/
```

---

# Patrón Repository

Nunca acceder directamente a la base de datos desde los servicios.

```text
Controller

↓

Use Case

↓

Repository

↓

Database
```

---

# Patrón Use Cases

Toda lógica de negocio vivirá aquí.

Ejemplo

RegisterExpenseUseCase

CreateGoalUseCase

CalculateDebtUseCase

GenerateAIReportUseCase

---

# API

Arquitectura REST.

Versionada.

```text
/api/v1
```

---

Ejemplo

```text
POST /auth/login

POST /expenses

GET /expenses

PUT /expenses/{id}

DELETE /expenses/{id}
```

---

# Comunicación

Frontend

↓

REST

↓

Backend

↓

Repository

↓

PostgreSQL

---

# Autenticación

JWT Access Token

Refresh Token

Tiempo

Access

15 minutos

Refresh

30 días

---

# Autorización

Middleware

Validaciones

- Usuario autenticado
- Pareja vinculada
- Propietario del recurso

---

# Manejo de Errores

Nunca retornar excepciones internas.

Formato

```json
{
    "success": false,
    "message": "Movimiento no encontrado."
}
```

---

# Manejo de Estados

Flutter utilizará Riverpod.

Estados

Loading

Success

Error

Empty

---

# Persistencia Local

Hive

Guardar

- Usuario
- Configuración
- Últimos movimientos
- Tema
- Idioma

---

# Sincronización

La aplicación funcionará parcialmente offline.

Cambios locales

↓

Cola

↓

Internet disponible

↓

Sincronizar

---

# IA

La IA será completamente desacoplada.

```text
AI Service

↓

Provider

↓

OpenAI

o

Proveedor futuro
```

Nunca depender directamente de OpenAI.

---

# Seguridad

HTTPS

JWT

Refresh Token

Hash Argon2

AES

Rate Limiting

CORS

Helmet

Headers seguros

---

# Logging

Logs estructurados.

Registrar

Login

Errores

Cambios

Pagos

IA

---

# Observabilidad

CloudWatch

Prometheus (futuro)

Grafana (futuro)

---

# Docker

Servicios

```text
postgres

backend

redis

pgadmin

nginx

worker

scheduler
```

---

# Variables de Entorno

Nunca hardcodear.

Ejemplo

```env
DATABASE_URL=

SECRET_KEY=

OPENAI_API_KEY=

REDIS_URL=

JWT_SECRET=

AWS_ACCESS_KEY=

AWS_SECRET_KEY=
```

---

# AWS

Arquitectura inicial

```text
Internet

↓

Route53

↓

CloudFront

↓

Load Balancer

↓

EC2

↓

Docker

↓

FastAPI

↓

PostgreSQL RDS

↓

Redis

↓

S3

↓

CloudWatch
```

---

# Almacenamiento

S3

Guardar

Facturas

Imágenes

Fotos

Exportaciones

---

# CDN

CloudFront

Para

Imágenes

Assets

---

# Firebase

Usos

Push Notifications

Analytics

Crashlytics

---

# Escalabilidad

Cuando aumenten los usuarios

Backend

↓

Múltiples instancias

↓

Load Balancer

↓

Redis Compartido

↓

PostgreSQL

---

# CI/CD

GitHub

↓

Tests

↓

Lint

↓

Build

↓

Docker Image

↓

Deploy AWS

---

# Testing

Frontend

Widget Tests

Golden Tests

Integration Tests

Backend

Pytest

Coverage

Mocks

---

# Dependencias

Nunca una Feature podrá importar otra Feature.

La comunicación siempre será mediante interfaces.

---

# Arquitectura de IA

```text
Usuario

↓

Pregunta

↓

AI Module

↓

Prompt Builder

↓

LLM Provider

↓

Respuesta

↓

Guardar Historial

↓

Mostrar Resultado
```

---

# Escalabilidad Futura

La arquitectura permitirá incorporar:

- Open Finance
- Bancos
- OCR
- Machine Learning
- Recomendaciones
- Marketplace
- Inversiones
- Tarjetas
- API pública
- Web
- Desktop

Sin modificar el núcleo.

---

# Convenciones

## Backend

snake_case

---

## Flutter

camelCase

PascalCase

---

## Base de Datos

snake_case

---

## Commits

Conventional Commits

Ejemplos

feat:

fix:

refactor:

docs:

test:

---

# Principio Final

La arquitectura deberá priorizar siempre:

- Simplicidad.
- Escalabilidad.
- Seguridad.
- Reutilización.
- Alto rendimiento.
- Bajo acoplamiento.
- Alta cohesión.

Toda nueva funcionalidad deberá integrarse respetando estos principios sin comprometer la estabilidad del sistema.