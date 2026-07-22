# 🗄️ Together

# Documento 07 — Diseño de Base de Datos

**Versión:** 1.0

**Estado:** Aprobado

---

# Objetivo

Este documento define el diseño completo de la base de datos de Together.

La base de datos debe ser:

- Escalable
- Segura
- Normalizada
- Fácil de mantener
- Optimizada para consultas analíticas
- Preparada para nuevas funcionalidades

Motor de Base de Datos:

**PostgreSQL 16+**

---

# Convenciones

## Llaves primarias

Todas las tablas utilizarán:

UUID

Ejemplo

id UUID PRIMARY KEY

---

## Auditoría

Todas las tablas tendrán:

created_at

updated_at

deleted_at (Soft Delete)

created_by (cuando aplique)

updated_by (cuando aplique)

---

## Fechas

Siempre

TIMESTAMP WITH TIME ZONE

---

## Eliminación

Nunca DELETE físico.

Siempre Soft Delete.

---

# Modelo General

```text
USERS
 │
 ├───────────────┐
 │               │
COUPLES      USER_SETTINGS
 │
 │
 ├──────────────┐
 │              │
SHARED_EXPENSES SHARED_INCOMES
 │              │
 │              │
DEBTS       CONTRIBUTIONS
 │
GOALS
 │
GOAL_CONTRIBUTIONS

USERS
 │
 ├──────────────┐
 │              │
PERSONAL_EXPENSES
PERSONAL_INCOMES
 │
BUDGETS

AI

NOTIFICATIONS

REMINDERS

CHAT

REPORTS

FILES
```

---

# Tabla 1

## users

Representa cada usuario registrado.

Campos

- id
- first_name
- last_name
- email
- password_hash
- avatar_url
- birth_date
- phone
- language
- currency
- timezone
- is_verified
- last_login
- created_at
- updated_at
- deleted_at

---

# Tabla 2

## user_settings

Configuraciones personales.

Campos

- user_id
- theme
- biometric_enabled
- notifications_enabled
- reminder_enabled
- ai_enabled
- default_home_screen

---

# Tabla 3

## couples

Representa la relación entre dos usuarios.

Campos

- id
- partner_one_id
- partner_two_id
- invitation_code
- status

Estados

Pending

Accepted

Rejected

Separated

---

# Tabla 4

## personal_categories

Categorías personales.

Ejemplo

Comida

Transporte

Salud

Educación

Tecnología

---

Campos

- id
- user_id
- name
- icon
- color

---

# Tabla 5

## personal_expenses

Todos los gastos privados.

Campos

- id
- user_id
- category_id
- amount
- description
- payment_method_id
- location
- attachment_id
- expense_date

---

# Tabla 6

## personal_incomes

Todos los ingresos privados.

Campos

- id
- user_id
- category_id
- amount
- description
- income_date

---

# Tabla 7

## shared_categories

Categorías compartidas.

Mercado

Viajes

Netflix

Mascotas

Arriendo

Servicios

---

# Tabla 8

## shared_expenses

Gastos compartidos.

Campos

- id
- couple_id
- category_id
- amount
- paid_by
- split_type
- notes
- attachment_id
- expense_date

---

# Tabla 9

## shared_income

Ingresos compartidos.

Ejemplo

Venta conjunta.

Negocio.

---

# Tabla 10

## debts

Controla cuánto debe cada integrante.

Campos

- debtor_id
- creditor_id
- shared_expense_id
- amount
- status

Estados

Pending

Paid

Cancelled

---

# Tabla 11

## payment_methods

Métodos de pago.

Ejemplos

Efectivo

Nequi

Daviplata

Bancolombia

Tarjeta Crédito

Tarjeta Débito

---

# Tabla 12

## goals

Metas compartidas.

Campos

- id
- couple_id
- title
- description
- image
- target_amount
- current_amount
- target_date
- status

---

# Tabla 13

## goal_contributions

Aportes a metas.

Campos

- goal_id
- user_id
- amount
- contribution_date

---

# Tabla 14

## budgets

Presupuestos.

Campos

- user_id
- category_id
- amount
- month
- year

---

# Tabla 15

## reminders

Recordatorios.

Campos

- user_id
- title
- description
- reminder_date
- repeat_type
- status

---

# Tabla 16

## notifications

Notificaciones.

Campos

- user_id
- type
- title
- body
- is_read

---

# Tabla 17

## reports

Historial de reportes generados.

Campos

- user_id
- report_type
- filters
- generated_at
- file_url

---

# Tabla 18

## files

Archivos.

Campos

- owner_id
- type
- storage_url
- mime_type
- size

---

# Tabla 19

## ai_conversations

Historial del chat IA.

Campos

- user_id
- title
- created_at

---

# Tabla 20

## ai_messages

Mensajes IA.

Campos

- conversation_id
- role
- content
- tokens
- created_at

---

# Tabla 21

## ai_insights

Recomendaciones generadas.

Campos

- user_id
- title
- description
- priority
- created_at

---

# Tabla 22

## recurring_transactions

Movimientos automáticos.

Campos

- user_id
- type
- frequency
- next_execution

---

# Tabla 23

## subscriptions

Suscripciones.

Netflix

Spotify

Prime

Disney

---

# Tabla 24

## audit_logs

Registro de acciones críticas.

Campos

- user_id
- action
- table_name
- record_id
- ip_address
- user_agent

---

# Tabla 25

## sessions

Sesiones activas.

Campos

- user_id
- refresh_token
- expires_at
- device
- ip

---

# Tabla 26

## login_history

Historial de inicio de sesión.

---

# Tabla 27

## devices

Dispositivos registrados.

---

# Tabla 28

## user_preferences

Preferencias avanzadas.

---

# Tabla 29

## achievements

Gamificación.

---

# Tabla 30

## user_achievements

Logros obtenidos.

---

# Tabla 31

## couple_statistics

KPIs precalculados.

Campos

- total_income
- total_expenses
- total_saved
- score
- updated_at

---

# Tabla 32

## monthly_statistics

KPIs mensuales.

---

# Tabla 33

## financial_predictions

Predicciones IA.

---

# Tabla 34

## expense_tags

Etiquetas.

Ejemplo

Vacaciones

Trabajo

Casa

Urgente

---

# Tabla 35

## expense_tag_relation

Relación N:M

Expenses

Tags

---

# Tabla 36

## chat_rooms

Canal privado de pareja.

---

# Tabla 37

## chat_messages

Mensajes.

Texto

Imagen

Audio

Sticker

---

# Tabla 38

## exports

Historial de exportaciones.

PDF

Excel

CSV

---

# Tabla 39

## currencies

Monedas soportadas.

---

# Tabla 40

## exchange_rates

Historial de tasas de cambio.

---

# Relaciones Principales

Users

↓

Couples

↓

Shared Expenses

↓

Debts

↓

Goals

↓

Goal Contributions

---

Users

↓

Personal Expenses

↓

Categories

↓

Budgets

↓

Reports

↓

Statistics

---

# Índices

Crear índices sobre:

email

couple_id

user_id

expense_date

goal_id

status

created_at

category_id

notification.user_id

---

# Restricciones

Email único.

No permitir montos negativos.

No permitir metas menores a cero.

No permitir gastos sin propietario.

No permitir una pareja con más de dos integrantes.

No permitir movimientos futuros cuando no correspondan.

---

# Vistas Materializadas

Crear vistas para:

Dashboard

Resumen mensual

Resumen anual

KPIs

Top categorías

Top gastos

---

# Triggers

Actualizar automáticamente:

Saldo

KPIs

Progreso metas

Score financiero

Dashboard

---

# Particionamiento (Futuro)

Particionar:

personal_expenses

shared_expenses

notifications

audit_logs

Por año.

---

# Estrategia de Migraciones

Alembic.

Una migración por feature.

Nunca modificar migraciones antiguas en producción.

---

# Convenciones de Nombres

Tablas

snake_case

Columnas

snake_case

Índices

idx_table_column

Llaves Foráneas

fk_table_reference

---

# Resumen

## Total de tablas

40

## Relaciones

Más de 70 relaciones

## Tipo

OLTP optimizada para:

- Aplicación móvil
- Reportes
- IA
- Analítica
- Escalabilidad

Esta estructura permitirá evolucionar Together desde un MVP hasta una plataforma financiera completa sin rediseñar la base de datos.