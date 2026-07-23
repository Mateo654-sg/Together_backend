# ⚙️ Together

# Documento 03 — Requerimientos No Funcionales

Versión: 1.0

Estado: Aprobado

---

# Objetivo

Este documento define todos los requisitos de calidad que debe cumplir Together.

Estos requerimientos no describen funcionalidades, sino la forma en que el sistema debe comportarse.

---

# NFR-001 Arquitectura

La aplicación deberá construirse siguiendo una arquitectura limpia (Clean Architecture).

Capas:

- Presentation
- Application
- Domain
- Infrastructure

Nunca se permitirá acceso directo desde la UI hacia la base de datos.

---

# NFR-002 Escalabilidad

La arquitectura deberá soportar:

- Más de 1.000.000 usuarios.
- Multi región.
- Nuevos módulos sin modificar el núcleo.
- Integraciones bancarias futuras.

---

# NFR-003 Rendimiento

Tiempo máximo de carga:

Splash Screen

< 2 segundos

Dashboard

< 1 segundo

Lista de movimientos

< 500 ms

Gráficas

< 700 ms

---

# NFR-004 Disponibilidad

Disponibilidad mínima

99.9%

---

# NFR-005 Seguridad

Toda comunicación deberá realizarse mediante HTTPS.

TLS 1.3

Nunca HTTP.

---

# NFR-006 Autenticación

JWT

Refresh Token

Expiración automática.

---

# NFR-007 Autorización

Cada endpoint deberá validar permisos.

Nunca confiar en el Frontend.

---

# NFR-008 Encriptación

Contraseñas

Argon2

Datos sensibles

AES-256

---

# NFR-009 Privacidad

Las finanzas personales jamás podrán ser visibles para la pareja.

Únicamente:

- Gastos compartidos
- Metas compartidas
- Fondo común

---

# NFR-010 Logs

Registrar:

Inicio de sesión

Errores

Cambios importantes

Intentos fallidos

Operaciones críticas

---

# NFR-011 Auditoría

Guardar historial de:

Cambios

Eliminaciones

Ediciones

---

# NFR-012 Disponibilidad Offline

El usuario podrá consultar:

Últimos movimientos

Dashboard

Metas

Sin conexión.

Los cambios se sincronizarán automáticamente.

---

# NFR-013 UX

Registrar un gasto no debe tomar más de tres pasos.

---

# NFR-014 Accesibilidad

Modo oscuro.

Modo claro.

Contraste AA.

Tamaño de fuente configurable.

---

# NFR-015 Compatibilidad

Android

iOS

Tablet

Web

---

# NFR-016 Internacionalización

Soportar:

Español

Inglés


---

# NFR-017 Monedas

COP

USD

EUR

MXN

BRL

---

# NFR-018 Base de datos

PostgreSQL.

Normalización hasta 3FN.

Índices en columnas de búsqueda.

Soft Delete.

UUID como llave primaria.

---

# NFR-019 API

RESTful.

JSON.

Versionada.

Ejemplo:

/api/v1

---

# NFR-020 Calidad de código

Principios SOLID.

DRY.

KISS.

Clean Code.

---

# NFR-021 Testing

Cobertura mínima

90%

Tipos:

- Unitarias
- Integración
- Widgets
- End to End

---

# NFR-022 Observabilidad

Integración con:

Logs

Métricas

Trazas

---

# NFR-023 CI/CD

Cada Pull Request ejecutará:

Lint

Tests

Build

Coverage

---

# NFR-024 Documentación

Swagger

OpenAPI

README

Arquitectura

Base de datos

---

# NFR-025 Backups

Backups automáticos diarios.

Retención mínima:

30 días.

---

# NFR-026 Mantenibilidad

Todo módulo nuevo deberá implementarse sin modificar módulos existentes.

---

# NFR-027 Animaciones

Animaciones inferiores a 250 ms.

Nunca bloquearán la interfaz.

---

# NFR-028 Consumo energético

Optimizar animaciones.

Reducir reconstrucciones innecesarias.

Evitar consumo excesivo de batería.

---

# NFR-029 Escalabilidad IA

La IA deberá ser desacoplada.

Debe poder cambiarse OpenAI por otro proveedor sin afectar el sistema.

---

# NFR-030 Principio General

Toda nueva funcionalidad deberá cumplir:

- Seguridad
- Escalabilidad
- Simplicidad
- Elegancia
- Alto rendimiento