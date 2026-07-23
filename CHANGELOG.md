# Changelog

Todos los cambios notables en Together Backend se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y el proyecto adherce a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] - 2026-07-22

### Added

#### Auth (Módulo 1)
- Registro de usuario con validación de contraseña fuerte
- Login con retorno de access y refresh tokens
- Refresh token con rotación
- Logout (revocación de token)

#### Users (Módulo 1b)
- Consulta de perfil del usuario
- Edición de información personal
- Eliminación de cuenta (soft delete)
- Gestión de configuración (tema, idioma, moneda)
- Actualización de avatar
- Estadísticas personales
- Cambio de contraseña
- Historial de sesiones

#### Couples (Módulo 2)
- Crear invitación con código
- Aceptar invitación
- Rechazar invitación
- Consultar estado de la pareja
- Desvincular pareja

#### Personal Finances (Módulo 3)
- CRUD de categorías personales
- CRUD de gastos personales
- CRUD de ingresos personales
- Balance personal

#### Shared Finances (Módulo 4)
- CRUD de gastos compartidos
- CRUD de ingresos compartidos
- Gestión de deudas
- Balance de pareja

#### Goals (Módulo 5)
- CRUD de metas financieras
- Contribuir a una meta
- Historial de contribuciones
- Estadísticas de metas

#### Budgets (Módulo 6)
- CRUD de presupuestos
- Alertas de presupuesto (80%, 90%, 100%)

#### Dashboard (Módulo 7)
- Dashboard personal
- Dashboard de pareja

#### Reports & Statistics (Módulo 8)
- Generación de reportes
- Listado y descarga de reportes
- Estadísticas mensuales
- Estadísticas personales

#### AI Assistant (Módulo 9)
- Chat con asistente financiero
- Análisis de gastos
- Predicciones financieras
- Score de salud financiera
- Insights y recomendaciones
- Resúmenes financieros
- Simulador financiero
- Historial de interacciones

#### Reminders (Módulo 10)
- CRUD de recordatorios
- Marcar como completado

#### Chat (Módulo 12 - 14)
- Enviar mensajes de texto
- Enviar emojis
- Enviar mensajes motivacionales
- Compartir metas y movimientos
- Eliminar mensajes

#### Notifications (Módulo 15)
- Listar notificaciones
- Marcar como leída
- Marcar todas como leídas
- Eliminar notificación

### Infrastructure
- FastAPI + SQLAlchemy 2 async + Alembic
- PostgreSQL 16 con UUID primary keys
- Redis para caché
- JWT (Access 15min / Refresh 30d con rotación)
- Argon2id para hashing de contraseñas
- Docker multi-stage build
- docker-compose para desarrollo
- 9 migraciones de Alembic
- 16 archivos de tests de integración
- Ruff para linting
- Clean Architecture con Repository Pattern
