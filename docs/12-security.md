# 🔒 Together

# Documento 12 — Seguridad

**Versión:** 1.0

**Estado:** Aprobado

**Última actualización:** 2026

---

# Objetivo

Este documento define la estrategia integral de seguridad para Together.

La seguridad no será un módulo independiente.

Será un principio transversal presente en toda la aplicación.

Todo componente desarrollado deberá cumplir los lineamientos definidos en este documento.

---

# Principios

Together seguirá los principios de:

- Zero Trust
- Least Privilege
- Defense in Depth
- Secure by Design
- Privacy by Design

---

# Objetivos

Proteger:

- Información financiera
- Datos personales
- Historial financiero
- Conversaciones
- Tokens
- Archivos
- Fotografías
- Reportes

---

# Arquitectura de Seguridad

```text
Usuario

↓

HTTPS

↓

CloudFront

↓

AWS WAF

↓

Load Balancer

↓

FastAPI

↓

Authentication

↓

Authorization

↓

Business Layer

↓

PostgreSQL
```

---

# Autenticación

Sistema

JWT

Access Token

Refresh Token

---

## Access Token

Duración

15 minutos

---

## Refresh Token

30 días

---

## Rotación

Cada Refresh Token utilizado genera uno nuevo.

El anterior queda invalidado.

---

# Login

Métodos

- Correo
- Google OAuth
- Apple Sign In (iOS)

---

# Contraseñas

Nunca almacenar texto plano.

Hash

Argon2id

---

Configuración mínima

Memory Cost

64 MB

Iterations

4

Parallelism

2

---

Longitud mínima

12 caracteres

---

Debe contener

- Mayúscula
- Minúscula
- Número
- Símbolo

---

No permitir

123456

password

qwerty

fechas

nombre

correo

---

# Autorización

Modelo

RBAC

Roles

- User
- Admin
- Super Admin

---

Permisos

Cada endpoint validará

- Usuario autenticado
- Propietario del recurso
- Estado de la pareja
- Rol

---

Ejemplo

Usuario A

No podrá consultar

Finanzas personales

del Usuario B.

---

# Seguridad API

Todos los endpoints

HTTPS obligatorio.

---

Headers

Authorization

Bearer Token

---

Content-Type

application/json

---

# Rate Limiting

Login

5 intentos/min

---

Register

5/min

---

IA

20/min

---

API General

500/min

---

# CORS

Permitir únicamente

Frontend oficial

Dominio producción

Dominio desarrollo

---

Nunca permitir

*

---

# CSRF

No aplica al JWT.

Sin embargo,

los Refresh Tokens deberán utilizar

Cookies HttpOnly

cuando exista cliente web.

---

# XSS

Escapar

Texto

Comentarios

Chat

Notas

---

Nunca renderizar HTML.

---

# SQL Injection

Toda consulta

SQLAlchemy ORM.

Nunca concatenar SQL.

---

# Validaciones

Backend

Pydantic

---

Frontend

Validaciones UX.

Nunca confiar únicamente en Flutter.

---

# Archivos

Tipos permitidos

jpg

jpeg

png

pdf

---

Máximo

10 MB

---

Escaneo antivirus

Futuro

ClamAV

---

# Información Sensible

Nunca almacenar

- Contraseñas
- Tokens externos
- Claves API
- Datos bancarios

---

# Variables de Entorno

Nunca subir al repositorio

.env

---

Ejemplo

DATABASE_URL

JWT_SECRET

OPENAI_API_KEY

AWS_SECRET

REDIS_URL

---

# Gestión de Secretos

Producción

AWS Secrets Manager

---

Desarrollo

.env

---

# Base de Datos

PostgreSQL

---

Conexión

SSL obligatorio.

---

Backups

Diarios.

---

Retención

30 días.

---

# Auditoría

Registrar

Login

Logout

Cambio contraseña

Eliminar cuenta

Eliminar meta

Pago deuda

Consultas IA

---

Tabla

audit_logs

---

Campos

Usuario

Acción

IP

Fecha

Dispositivo

---

# Historial de Sesiones

Mostrar

Dispositivo

IP

Ciudad aproximada

Fecha

Estado

---

Permitir

Cerrar sesión

de dispositivos remotos.

---

# Encriptación

AES-256

Para

Archivos sensibles

Datos privados

---

Hash

Argon2

---

TLS

1.3

---

# Cookies

HttpOnly

Secure

SameSite=Strict

---

# Seguridad Flutter

Nunca almacenar

JWT

en SharedPreferences.

---

Utilizar

Flutter Secure Storage

---

Información cacheada

Hive

Nunca datos sensibles.

---

# Root Detection

Detectar

Root

Jailbreak

---

Advertir al usuario.

---

# SSL Pinning

Implementar

Certificate Pinning

en producción.

---

# Logs

Nunca registrar

Contraseñas

Tokens

Datos personales

---

Sí registrar

Errores

Requests

Latencia

---

# Monitoreo

CloudWatch

Crashlytics

Firebase Analytics

---

# Alertas

Detectar

Muchos logins fallidos

↓

Bloquear temporalmente.

---

# Bloqueo

Después de

5 intentos

↓

15 minutos.

---

# Eliminación de Cuenta

Proceso

Confirmar contraseña

↓

Confirmación

↓

Soft Delete

↓

Retención 30 días

↓

Eliminación definitiva

---

# Privacidad

Cumplir

GDPR

CCPA

Ley 1581 de Colombia

---

El usuario podrá

Exportar datos

Eliminar datos

Solicitar copia

---

# IA

Nunca enviar

JWT

Contraseñas

Correos de terceros

Datos bancarios

---

Solo contexto financiero.

---

# Seguridad IA

Validar

Prompt Injection

Prompt Leakage

Sensitive Data Exposure

---

# Dependencias

Escaneo automático

Dependabot

Snyk

---

# CI/CD

Antes del Deploy

Ejecutar

Lint

Tests

Security Scan

Dependency Scan

Secrets Scan

---

# OWASP Top 10

Mitigar

A01 Broken Access Control

A02 Cryptographic Failures

A03 Injection

A04 Insecure Design

A05 Security Misconfiguration

A06 Vulnerable Components

A07 Authentication Failures

A08 Software Integrity Failures

A09 Logging Failures

A10 SSRF

---

# AWS

Servicios

CloudFront

AWS WAF

EC2

RDS

S3

Secrets Manager

CloudWatch

IAM

---

# IAM

Aplicar

Least Privilege

---

Cada servicio tendrá

su propio rol.

---

Nunca utilizar

Access Keys

hardcodeadas.

---

# Disponibilidad

Objetivo

99.9%

---

# Disaster Recovery

Backups

Automáticos

↓

RDS Snapshot

↓

Restauración

↓

Validación

---

RPO

15 minutos

---

RTO

2 horas

---

# Seguridad del Código

Aplicar

SOLID

Clean Code

Code Review

Static Analysis

---

Herramientas

Ruff

Bandit

SonarQube

---

# Pentesting

Antes de producción

Realizar

- Escaneo OWASP ZAP
- Análisis de vulnerabilidades
- Pruebas de autenticación
- Pruebas de autorización
- SQL Injection
- XSS
- IDOR
- SSRF

---

# Logs de Seguridad

Registrar

Inicio de sesión

Intentos fallidos

Cambio contraseña

Cambio correo

Eliminación cuenta

Creación pareja

Desvinculación

Exportación datos

---

# Alertas Críticas

Notificar al usuario cuando

- Se inicia sesión desde un nuevo dispositivo.
- Se cambia la contraseña.
- Se cambia el correo.
- Se elimina una meta.
- Se exportan datos.
- Se detecta actividad sospechosa.

---

# Checklist antes de Producción

- HTTPS habilitado
- TLS 1.3
- JWT funcionando
- Refresh Token validado
- CORS configurado
- Rate Limiting activo
- WAF habilitado
- IAM revisado
- Secrets Manager configurado
- Backups automáticos
- Auditoría funcionando
- Logs centralizados
- Crashlytics activo
- Dependabot activo
- Snyk activo
- OWASP ZAP ejecutado
- Cobertura de pruebas ≥ 90%

---

# Principio Final

La confianza es el activo más importante de Together.

Los usuarios compartirán información financiera privada y, por lo tanto, toda decisión técnica deberá priorizar la protección de sus datos.

La seguridad no será considerada una fase del desarrollo, sino un requisito permanente presente desde el diseño, la implementación, las pruebas y la operación del sistema.