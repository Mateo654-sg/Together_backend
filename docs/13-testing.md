# 🧪 Together

# Documento 13 — Testing Strategy

**Versión:** 1.0

**Estado:** Aprobado

**Última actualización:** 2026

---

# Objetivo

Este documento define la estrategia completa de pruebas para Together.

El objetivo no es únicamente detectar errores.

El objetivo es garantizar:

- Calidad
- Estabilidad
- Seguridad
- Escalabilidad
- Rendimiento

antes de cada despliegue.

---

# Filosofía

Cada línea de código debe poder demostrarse.

Todo cambio debe estar respaldado por pruebas.

No se aceptarán funcionalidades sin cobertura de pruebas.

---

# Objetivos

Garantizar

✔ El sistema funciona correctamente.

✔ Los datos financieros son consistentes.

✔ La IA responde correctamente.

✔ Las APIs son seguras.

✔ El Frontend mantiene la experiencia esperada.

✔ Los cambios futuros no rompen funcionalidades existentes.

---

# Pirámide de Testing

```text
               E2E

         Integration Tests

        Component / Widget Tests

          Unit Tests
```

Prioridad

70%

Unit Tests

20%

Integration

10%

E2E

---

# Cobertura

Cobertura mínima

Backend

90%

Frontend

90%

Global

90%

Nunca disminuir la cobertura.

---

# Herramientas

Backend

Pytest

Pytest Asyncio

Factory Boy

HTTPX

Coverage.py

---

Frontend

flutter_test

integration_test

mocktail

golden_toolkit

patrol (futuro)

---

CI/CD

GitHub Actions

Codecov

---

# Tipos de Pruebas

## Unitarias

Validan

- Funciones
- Casos de uso
- Reglas financieras
- Utilidades
- Servicios

Nunca accederán a la base de datos.

---

Ejemplo

```python
calculateDebt()

↓

Resultado esperado
```

---

# Casos de Uso

Cada UseCase tendrá pruebas.

Ejemplos

RegisterExpense

DeleteExpense

CreateGoal

PayDebt

GenerateFinancialScore

CreateReminder

---

# Repository Tests

Validar

Consultas

Persistencia

Mapeos

Conversión DTO

---

# API Tests

Cada endpoint tendrá pruebas.

Ejemplo

POST /expenses

GET /expenses

PUT /expenses

DELETE /expenses

---

Casos

✔ Éxito

✔ Error

✔ Permisos

✔ Validaciones

✔ Datos inválidos

---

# Integration Tests

Validan

Flutter

↓

FastAPI

↓

PostgreSQL

---

No utilizar mocks.

---

Validar

Autenticación

JWT

Refresh Token

CRUD

Metas

Reportes

IA

---

# Widget Tests

Cada Widget reutilizable tendrá pruebas.

Ejemplos

PrimaryButton

ExpenseCard

GoalCard

BudgetCard

DashboardCard

InsightCard

---

Validar

Render

Estados

Clicks

Errores

---

# Golden Tests

Comparar

UI actual

↓

Imagen esperada

---

Pantallas

Dashboard

Login

Expense Detail

Goals

AI

---

Evitar cambios visuales accidentales.

---

# Integration Flutter

Flujos completos.

Ejemplo

Login

↓

Dashboard

↓

Registrar gasto

↓

Actualizar dashboard

↓

Cerrar sesión

---

# End to End

Automatizar

Registro

Login

Crear pareja

Registrar gasto

Registrar meta

Pagar deuda

Consultar IA

Exportar PDF

Cerrar sesión

---

# Smoke Tests

Después de cada Deploy.

Validar

API disponible

DB disponible

Redis disponible

Firebase disponible

---

# Regression Tests

Ejecutar

Antes de cada Release.

---

Validar

Todo el MVP.

---

# Performance Tests

Herramientas

Locust

k6

---

Escenarios

100 usuarios

500 usuarios

1000 usuarios

5000 usuarios

10000 usuarios

---

Métricas

Tiempo respuesta

CPU

RAM

Errores

---

Objetivos

API

<300 ms

Dashboard

<500 ms

Login

<1 s

---

# Stress Tests

Incrementar carga

↓

Detectar límite

↓

Validar recuperación.

---

# Load Tests

Usuarios simultáneos.

Consultar

Dashboard

IA

Metas

Reportes

---

# Security Tests

Validar

JWT

Permisos

SQL Injection

XSS

IDOR

Rate Limiting

CSRF (Web)

Headers

---

Herramientas

OWASP ZAP

Bandit

Snyk

---

# AI Tests

Validar

Prompts

Respuestas

Contexto

Predicciones

Insights

---

Ejemplo

Pregunta

```
¿Cuánto gasté este mes?
```

↓

Comparar

Respuesta IA

↓

Financial Rules Engine

---

Nunca aceptar

Hallucinations.

---

# OCR Tests

Facturas

Grandes

Pequeñas

Borrosas

Recortadas

Con IVA

Sin IVA

---

Validar

Monto

Fecha

Comercio

---

# Financial Rules Tests

Probar

Cálculo deuda

Cálculo metas

Score

KPIs

Presupuesto

Alertas

Predicciones

---

Debe existir

100% cobertura.

---

# Data Integrity Tests

Validar

No montos negativos.

No usuarios duplicados.

No parejas inválidas.

No metas inconsistentes.

---

# Database Tests

Validar

Índices

Triggers

Views

Constraints

FK

---

# Offline Tests

Flutter

Sin Internet

↓

Registrar gasto

↓

Reconectar

↓

Sincronizar

---

# Notification Tests

Push

Foreground

Background

App cerrada

---

# Accessibility Tests

Contraste

Screen Reader

Escalado

Focus

---

# Exploratory Testing

Realizado manualmente

Antes de cada Release.

---

# QA Checklist

Antes de Merge

- Tests pasan.
- Lint OK.
- Coverage >90%.
- Sin vulnerabilidades.
- Sin warnings.

---

# Definition of Done

Una funcionalidad estará terminada únicamente si

- Está implementada.
- Tiene Unit Tests.
- Tiene Integration Tests.
- Tiene documentación.
- Fue revisada.
- Pasó CI.
- Fue aprobada.

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

Build Docker

↓

Deploy
```

---

# Reportes

Cada ejecución generará

Coverage

Tiempo

Errores

Logs

Artifacts

---

# Convenciones

Archivos

Backend

```
test_users.py

test_expenses.py

test_goals.py
```

Flutter

```
expense_page_test.dart

goal_card_test.dart

dashboard_test.dart
```

---

# Mocks

Solo utilizar

Unit Tests.

Nunca

Integration Tests.

---

# Datos de Prueba

Factory Boy

Fixtures

Seeds

Nunca utilizar

Datos reales.

---

# Entornos

Local

Development

Testing

Staging

Production

---

# Release Checklist

Antes de Producción

- Unit Tests ✔
- Widget Tests ✔
- Integration ✔
- Golden ✔
- E2E ✔
- Load ✔
- Security ✔
- Coverage ✔
- QA ✔
- Product Owner ✔

---

# KPIs de Calidad

Cobertura

≥90%

Bugs críticos

0

Crash Rate

<0.1%

Tiempo promedio de respuesta

<300 ms

Build exitosos

100%

---

# Testing Continuo

Las pruebas deberán ejecutarse automáticamente en:

- Pull Request
- Merge a main
- Release
- Deploy a Staging
- Deploy a Production

---

# Cultura de Calidad

La calidad no es responsabilidad exclusiva del QA.

Es responsabilidad de:

- Backend
- Frontend
- DevOps
- Product Owner
- QA
- Arquitectura

Todos los miembros del equipo son responsables de mantener la estabilidad del producto.

---

# Principio Final

Together manejará información financiera sensible.

Por esta razón, ninguna funcionalidad podrá llegar a producción sin haber sido validada mediante una estrategia de pruebas automatizadas y manuales.

El objetivo no es simplemente encontrar errores, sino construir un producto confiable, estable y preparado para crecer sin comprometer la experiencia del usuario.