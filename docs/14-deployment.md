# 🚀 Together

# Documento 14 — Deployment & DevOps

**Versión:** 1.0

**Estado:** Aprobado

**Arquitectura:** Cloud Native

**Proveedor Cloud:** AWS

---

# Objetivo

Este documento define la estrategia completa de despliegue de Together.

El objetivo es garantizar que el sistema sea:

- Escalable
- Seguro
- Automatizado
- Observado
- Fácil de mantener
- Preparado para crecimiento

---

# Ambientes

La aplicación contará con cinco ambientes.

```text
Local

↓

Development

↓

Testing

↓

Staging

↓

Production
```

Cada ambiente tendrá:

- Variables propias
- Base de datos independiente
- Recursos independientes
- Logs independientes

---

# Arquitectura Cloud

```text
                     Internet

                         │

                    Route53 DNS

                         │

                    CloudFront CDN

                         │

                      AWS WAF

                         │

                 Application Load Balancer

                         │

                 EC2 Auto Scaling Group

                         │

              Docker Containers (FastAPI)

         ┌────────────┬────────────┬────────────┐
         │            │            │
      Backend      Scheduler     Workers
         │            │            │
         └────────────┴────────────┘
                     │

     ┌───────────────┼───────────────────┐
     │               │                   │
 PostgreSQL RDS   Redis Elasticache     S3

                     │

              Firebase Cloud Messaging

                     │

                Flutter Mobile App
```

---

# Tecnologías

## Backend

FastAPI

---

## Frontend

Flutter

---

## Base de Datos

PostgreSQL

---

## Cache

Redis

---

## Storage

Amazon S3

---

## CDN

CloudFront

---

## DNS

Route53

---

## Seguridad

AWS WAF

---

## Monitoreo

CloudWatch

---

## Contenedores

Docker

Docker Compose

---

## CI/CD

GitHub Actions

---

# Docker

Todos los servicios estarán dockerizados.

---

## Servicios

```text
backend

postgres

redis

nginx

worker

scheduler

pgadmin
```

---

# Dockerfile

Cada servicio tendrá:

- Imagen ligera (python:3.12-slim)
- Usuario no root
- Multi-stage build
- Healthcheck
- Variables por entorno

---

# Docker Compose

Archivos

```text
docker-compose.dev.yml

docker-compose.test.yml

docker-compose.prod.yml
```

---

# Variables de Entorno

Nunca se almacenarán en Git.

Ejemplo

```env
APP_ENV=

DATABASE_URL=

REDIS_URL=

JWT_SECRET=

OPENAI_API_KEY=

AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

S3_BUCKET=

FCM_SERVER_KEY=
```

---

# Secrets

Producción

AWS Secrets Manager

---

Desarrollo

.env

---

# Base de Datos

Amazon RDS

PostgreSQL

Backups automáticos

Snapshots

Multi-AZ (Producción)

---

# Redis

Elasticache

Usos

- Cache
- Sesiones
- Rate Limiting
- IA
- Dashboard

---

# S3

Almacenará

- Facturas
- Avatares
- Reportes
- Exportaciones
- Archivos OCR

Nunca archivos temporales.

---

# CloudFront

Distribuirá

Imágenes

Archivos

Assets

Exportaciones

---

# Nginx

Responsabilidades

- Reverse Proxy
- Compresión Gzip
- HTTPS Redirect
- Headers de Seguridad
- Rate Limiting adicional

---

# HTTPS

Certificados

AWS Certificate Manager

TLS 1.3

Obligatorio

---

# Dominios

Producción

```text
together.app

api.together.app

cdn.together.app
```

---

Desarrollo

```text
dev.together.app

api-dev.together.app
```

---

# Git Flow

```text
main

develop

feature/*

release/*

hotfix/*
```

---

# GitHub Actions

Pipeline

```text
Push

↓

Lint

↓

Backend Tests

↓

Frontend Tests

↓

Coverage

↓

Security Scan

↓

Docker Build

↓

Push Container Registry

↓

Deploy

↓

Smoke Tests

↓

Notificación
```

---

# Registro de Imágenes

Repositorio

Amazon ECR

---

# Estrategia de Deploy

Development

Deploy automático

---

Staging

Deploy automático

---

Production

Deploy manual aprobado

---

# Blue/Green Deployment

Producción utilizará

Blue

↓

Validación

↓

Switch

↓

Green

---

Permite rollback inmediato.

---

# Rollback

Si falla un despliegue

↓

Rollback automático

↓

Versión anterior

↓

Notificación

---

# Health Checks

Backend

```text
GET /health
```

Respuesta

```json
{
  "status":"healthy"
}
```

---

## Checks

API

DB

Redis

Storage

AI Provider

Firebase

---

# Monitoreo

CloudWatch

Registrar

CPU

RAM

Requests

Errores

Latencia

Disco

---

# Alertas

Enviar alerta cuando

CPU > 80%

RAM > 85%

Errores 5xx

RDS caída

Redis caída

AI caída

---

# Logging

Logs estructurados

Formato

JSON

---

Registrar

Requests

Errores

Usuario

Tiempo respuesta

IP

Endpoint

---

# Crash Reporting

Frontend

Firebase Crashlytics

Backend

CloudWatch

---

# Métricas

Disponibilidad

99.9%

---

Tiempo respuesta

<300 ms

---

Tiempo despliegue

<10 min

---

Tiempo rollback

<2 min

---

# Auto Scaling

Reglas

CPU >70%

↓

Nueva instancia

CPU <30%

↓

Eliminar instancia

---

# Backups

RDS

Cada día

---

S3

Versionado habilitado

---

Retención

30 días

---

# Disaster Recovery

RPO

15 minutos

---

RTO

2 horas

---

# Seguridad

AWS WAF

Rate Limiting

HTTPS

IAM

Security Groups

Secrets Manager

---

# IAM

Cada servicio tendrá

su propio rol.

Nunca compartir permisos.

---

# Terraform (Futuro)

Toda la infraestructura deberá migrarse a

Infrastructure as Code

Herramienta

Terraform

---

Estructura

```text
terraform/

network/

compute/

database/

storage/

security/

monitoring/
```

---

# Kubernetes (Futuro)

Cuando el crecimiento lo requiera

Migrar

Docker

↓

Amazon EKS

---

# Monitoreo Futuro

Prometheus

Grafana

Jaeger

OpenTelemetry

---

# Dependencias

Escaneo automático

Dependabot

Renovate

Snyk

---

# Release Process

```text
Merge Develop

↓

Deploy Staging

↓

QA

↓

Product Approval

↓

Deploy Production

↓

Smoke Tests

↓

Monitor

↓

Release
```

---

# Checklist Producción

- Docker Build OK
- Tests >90%
- Security Scan OK
- Variables configuradas
- Secrets cargados
- HTTPS activo
- WAF activo
- Backups activos
- Logs funcionando
- CloudWatch activo
- Crashlytics activo
- Health Checks OK
- Rollback probado

---

# Costos (MVP)

Infraestructura inicial

- EC2 t3.small
- PostgreSQL RDS db.t4g.micro
- ElastiCache Redis
- S3
- CloudFront
- Route53
- ACM
- CloudWatch

Objetivo

Mantener el costo inicial bajo mientras se garantiza escalabilidad.

---

# Roadmap DevOps

## MVP

Docker Compose

EC2

RDS

Redis

---

## Beta

CI/CD

CloudFront

S3

Monitoreo

---

## V1

Auto Scaling

Blue/Green

Secrets Manager

---

## V2

Terraform

EKS

Prometheus

Grafana

---

## V3

Arquitectura Multi-Región

Alta Disponibilidad Global

Disaster Recovery Automatizado

---

# Principio Final

El despliegue de Together debe ser completamente automatizado, reproducible y seguro.

Ningún cambio llegará a producción sin pasar por pruebas automatizadas, validaciones de seguridad y un pipeline de CI/CD.

La infraestructura deberá diseñarse desde el inicio con mentalidad **Cloud Native**, permitiendo que Together evolucione desde un MVP hasta una plataforma financiera de alcance internacional sin rediseñar su arquitectura principal.