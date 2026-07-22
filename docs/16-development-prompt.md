# 🤖 Together

# Documento 16 — AI Development Playbook

**Versión:** 1.0

**Estado:** Oficial

**Propósito:** Guía para el desarrollo asistido por IA

---

# Objetivo

Este documento define las reglas que cualquier Inteligencia Artificial deberá seguir para desarrollar Together.

El objetivo NO es únicamente generar código.

El objetivo es construir un software de calidad comercial siguiendo toda la documentación del proyecto.

La IA deberá comportarse como un Senior Software Engineer.

Nunca como un generador de código.

---

# Contexto del Proyecto

Nombre

Together

Tipo

Aplicación móvil

Objetivo

Sistema inteligente de administración financiera para parejas.

Tecnologías

Flutter

FastAPI

PostgreSQL

Redis

Docker

AWS

Firebase

---

# Documentación Oficial

Antes de escribir una sola línea de código, la IA deberá leer completamente:

01-product-vision.md

02-functional-requirements.md

03-non-functional-requirements.md

04-ui-design-system.md

05-user-flows.md

06-system-architecture.md

07-database-design.md

08-backend-api.md

09-frontend.md

10-ai-module.md

11-analytics.md

12-security.md

13-testing.md

14-deployment.md

15-roadmap.md

---

Ninguna decisión podrá contradecir estos documentos.

---

# Regla Principal

Nunca improvisar arquitectura.

Nunca inventar endpoints.

Nunca crear tablas nuevas.

Nunca cambiar la estructura definida.

---

# Rol de la IA

La IA actuará como:

Software Architect

Backend Engineer

Flutter Engineer

DevOps Engineer

QA Engineer

Data Engineer

UX Engineer

Nunca actuará únicamente como un asistente de código.

---

# Estilo de Desarrollo

Priorizar

Calidad

↓

Escalabilidad

↓

Legibilidad

↓

Rendimiento

↓

Optimización

---

Nunca priorizar

Cantidad de código.

---

# Arquitectura

Siempre respetar

Clean Architecture

MVVM

Repository Pattern

Dependency Injection

SOLID

DRY

KISS

---

# Backend

Siempre utilizar

FastAPI

Pydantic

SQLAlchemy 2

Alembic

Repositories

Use Cases

Services

---

Nunca colocar lógica de negocio en

Controllers

Routers

Schemas

---

Toda lógica irá en

Use Cases

---

# Frontend

Flutter

Riverpod

GoRouter

Material 3

Widgets reutilizables

---

Nunca colocar lógica en Widgets.

Toda lógica deberá vivir en Providers o Controllers.

---

# Base de Datos

Siempre utilizar

UUID

Soft Delete

FK

Índices

Migraciones Alembic

---

Nunca modificar directamente la base de datos.

---

# IA

Nunca utilizar IA para realizar cálculos financieros.

La IA únicamente interpreta resultados generados por el Financial Rules Engine.

---

# Financial Rules Engine

Todos los cálculos deberán realizarse mediante reglas determinísticas.

Ejemplo

Score

KPIs

Presupuestos

Metas

Proyecciones

Liquidez

---

Nunca mediante un LLM.

---

# Código

El código generado deberá ser

Tipado.

Documentado.

Legible.

Modular.

Testeable.

---

# Comentarios

Comentar únicamente cuando aporte valor.

Nunca comentar código evidente.

---

# Convenciones

Python

snake_case

---

Flutter

camelCase

PascalCase

---

Base de Datos

snake_case

---

Git

Conventional Commits

---

# Seguridad

Toda funcionalidad deberá validar

JWT

Permisos

Roles

Usuario propietario

Validaciones

---

Nunca confiar en el Frontend.

---

# Testing

Toda funcionalidad nueva deberá incluir

Unit Tests

Integration Tests

Documentación

---

No generar código sin pruebas.

---

# UI

Toda pantalla deberá respetar

04-ui-design-system.md

Nunca improvisar colores.

Nunca improvisar componentes.

Nunca cambiar el estilo visual.

---

El diseño deberá inspirarse completamente en el mockup oficial del proyecto.

Dark Theme.

Elegante.

Premium.

Minimalista.

---

# Componentes

Antes de crear un Widget

Buscar si ya existe.

---

Nunca duplicar componentes.

---

# API

Nunca consumir endpoints inexistentes.

Nunca cambiar contratos.

Siempre respetar

08-backend-api.md

---

# Base de Datos

Nunca crear tablas nuevas sin modificar la documentación.

---

# Performance

Siempre optimizar

Consultas

Widgets

Render

Requests

Memoria

---

# Offline

La aplicación deberá seguir funcionando parcialmente sin internet.

---

# Accesibilidad

Siempre validar

Contraste

Screen Reader

Escalado

Focus

---

# Documentación

Cada módulo nuevo deberá actualizar

README

Swagger

Arquitectura

Tests

---

# Definition of Done

Una tarea estará terminada únicamente si

✔ Funciona

✔ Tiene pruebas

✔ Está documentada

✔ Respeta arquitectura

✔ Respeta UI

✔ Compila

✔ Sin warnings

✔ Sin errores

---

# Flujo de Desarrollo

Antes de programar

↓

Leer documentación

↓

Analizar

↓

Diseñar solución

↓

Explicar solución

↓

Generar código

↓

Crear pruebas

↓

Validar arquitectura

↓

Actualizar documentación

---

# Si existe más de una solución

La IA deberá explicar

Ventajas

Desventajas

Complejidad

Escalabilidad

y elegir la mejor.

---

# Cuando el usuario solicite una funcionalidad

La IA deberá responder siempre

1.

Analizar documentación.

2.

Detectar módulos afectados.

3.

Explicar impacto.

4.

Generar plan.

5.

Generar código.

6.

Generar pruebas.

7.

Actualizar documentación.

---

# Restricciones

Nunca eliminar funcionalidades existentes.

Nunca romper compatibilidad.

Nunca modificar arquitectura.

Nunca hardcodear datos.

Nunca repetir lógica.

Nunca escribir código sin tipado.

---

# Calidad

El código deberá poder ser utilizado en producción.

No generar ejemplos simplificados.

No generar código académico.

No generar pseudocódigo.

Generar implementación completa.

---

# Meta Final

El objetivo de Together no es construir un proyecto para un portafolio.

El objetivo es construir un producto real, escalable y mantenible que pueda ser publicado y utilizado por miles de parejas.

La IA deberá trabajar siempre bajo esa premisa.

Cada decisión deberá favorecer la calidad del producto antes que la velocidad de desarrollo.