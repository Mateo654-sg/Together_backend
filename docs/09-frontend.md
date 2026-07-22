# 📱 Together

# Documento 09 — Frontend

**Versión:** 1.0

**Estado:** Aprobado

**Framework:** Flutter

**Lenguaje:** Dart

**Arquitectura:** MVVM + Clean Architecture

---

# Objetivo

Este documento define la arquitectura oficial del Frontend de Together.

Toda la aplicación deberá construirse siguiendo los principios de:

- Clean Architecture
- SOLID
- Material 3
- Responsive Design
- Componentes reutilizables
- Alto rendimiento
- Escalabilidad

---

# Filosofía

El Frontend debe sentirse como una aplicación premium.

No debe parecer una aplicación bancaria tradicional.

Debe transmitir:

❤️ Cercanía

💰 Organización

📊 Inteligencia

✨ Elegancia

---

# Stack Tecnológico

Framework

Flutter Stable

---

Lenguaje

Dart

---

Gestor de Estado

Riverpod

---

Rutas

GoRouter

---

Networking

Dio

---

Serialización

json_serializable

Freezed

---

Persistencia

Hive

Flutter Secure Storage

---

Internacionalización

Flutter Intl

---

Gráficas

fl_chart

---

Animaciones

Flutter Animate

Hero

Implicit Animations

---

Responsive

flutter_screenutil

---

Notificaciones

Firebase Messaging

---

Arquitectura

```text
lib/

├── app/
│
├── core/
│
├── features/
│
├── shared/
│
├── theme/
│
├── services/
│
├── routes/
│
└── main.dart
```

---

# Core

```text
core/

constants/

errors/

extensions/

helpers/

network/

storage/

theme/

utils/

widgets/
```

---

# Features

Cada módulo será independiente.

```text
features/

authentication/

dashboard/

expenses/

income/

goals/

budgets/

ai/

notifications/

profile/

settings/

shared/
```

---

Cada módulo tendrá

```text
expenses/

data/

domain/

presentation/
```

---

# Data

```text
data/

datasources/

models/

repositories/
```

---

# Domain

```text
domain/

entities/

repositories/

usecases/
```

---

# Presentation

```text
presentation/

pages/

widgets/

providers/

controllers/
```

---

# Shared

```text
shared/

buttons/

cards/

dialogs/

bottom_sheet/

charts/

animations/

inputs/

empty_states/

loaders/
```

---

# Rutas

GoRouter

```text
/

login

register

dashboard

expenses

expense-detail

goals

goal-detail

profile

settings

notifications

ai

chat

reports
```

---

# Navegación

Bottom Navigation

```text
🏠 Inicio

📄 Actividad

🎯 Metas

🤖 IA

👤 Perfil
```

Botón flotante

➕

Registrar Movimiento

---

# Manejo de Estado

Riverpod

Estados

Loading

Success

Error

Empty

Offline

---

Cada pantalla tendrá su propio Provider.

Ejemplo

DashboardProvider

ExpenseProvider

GoalProvider

AIProvider

NotificationProvider

---

# Comunicación

```text
Widget

↓

Provider

↓

UseCase

↓

Repository

↓

Remote Data Source

↓

API
```

Nunca consumir la API directamente desde la UI.

---

# Networking

Cliente único

Dio

Interceptors

JWT

Refresh Token

Logs

Retry

---

# Cache

Hive

Guardar

Usuario

Tema

Idioma

Configuración

Últimos movimientos

Dashboard

---

# Diseño Responsivo

Debe funcionar correctamente en

Android

iPhone

Tablet

Foldables

Web (futuro)

---

Breakpoints

Compact

Medium

Expanded

---

# Temas

Dark

Light

System

---

Los colores estarán definidos únicamente en

```text
theme/

colors.dart
```

Nunca usar colores hardcodeados.

---

# Tipografía

Poppins

Weights

Regular

Medium

SemiBold

Bold

---

# Componentes Reutilizables

Buttons

PrimaryButton

SecondaryButton

DangerButton

IconButton

FloatingButton

---

Cards

DashboardCard

ExpenseCard

GoalCard

BudgetCard

InsightCard

StatisticCard

ProfileCard

CoupleCard

ReminderCard

---

Inputs

TextInput

PasswordInput

SearchInput

MoneyInput

OTPInput

Dropdown

DatePicker

TimePicker

---

Dialogs

ConfirmationDialog

DeleteDialog

SuccessDialog

ErrorDialog

LoadingDialog

---

Bottom Sheets

ExpenseBottomSheet

IncomeBottomSheet

GoalBottomSheet

ReminderBottomSheet

---

# Dashboard

Widgets

Greeting

Balance Card

Income Card

Expense Card

Goal Card

Monthly Statistics

Recent Activity

AI Insights

Reminder List

Quick Actions

---

# Expenses

Pantallas

Expense List

Expense Detail

Create Expense

Edit Expense

Expense Filters

Expense Categories

---

# Goals

Pantallas

Goal List

Goal Detail

Goal Progress

Goal Contributions

Create Goal

---

# IA

Pantallas

AI Chat

Insights

Predictions

Recommendations

Financial Health

---

# Perfil

Pantallas

User

Partner

Preferences

Security

Appearance

Language

Currency

---

# Estados Vacíos

Cada Feature tendrá

EmptyState

Ejemplo

Sin gastos

Sin metas

Sin pareja

Sin notificaciones

Sin IA

---

# Estados de Error

Todas las pantallas tendrán

Retry Button

Mensaje amigable

Ilustración

---

# Loading

Skeleton Loading

Nunca Circular Progress únicamente.

---

# Animaciones

Duración

150 ms

250 ms

300 ms

Tipos

Fade

Hero

Slide

Scale

Opacity

Progress Animation

---

# Accesibilidad

Contraste WCAG AA

Text Scaling

Screen Reader

Semantics

Focus Navigation

---

# Internacionalización

Idiomas

Español

English

Português

---

Monedas

COP

USD

EUR

BRL

MXN

---

# Formato de Dinero

Ejemplo

$ 1.250.000

COP

---

# Validaciones

Formulario

Email

Contraseña

Nombre

Monto

Fecha

Número

Siempre en tiempo real.

---

# Gestión de Errores

Nunca mostrar

Exception

Stacktrace

Socket Error

HTTP Error

Siempre mostrar

"No pudimos completar la acción.

Intentemos nuevamente."

---

# Seguridad

Secure Storage

JWT

Refresh Token

Biometría

PIN

Ocultar información sensible

---

# Notificaciones

Firebase Cloud Messaging

Tipos

Reminder

Goal

Debt

Expense

Income

AI

---

# Rendimiento

Lazy Loading

Infinite Scroll

Pagination

Image Cache

Memoization

Const Widgets

RepaintBoundary

---

# Testing

Widget Test

Golden Test

Integration Test

Snapshot Test

---

Cobertura mínima

90%

---

# Convenciones

Widgets

PascalCase

Variables

camelCase

Archivos

snake_case.dart

---

# Estructura de una Feature

```text
expenses/

data/

models/

expense_model.dart

repositories/

expense_repository_impl.dart

datasources/

expense_remote_datasource.dart

domain/

entities/

expense.dart

repositories/

expense_repository.dart

usecases/

create_expense.dart

get_expenses.dart

delete_expense.dart

presentation/

pages/

expense_page.dart

expense_detail_page.dart

widgets/

expense_card.dart

expense_filter.dart

providers/

expense_provider.dart
```

---

# Principios de Desarrollo

Todo componente debe cumplir:

✔ Reutilizable

✔ Independiente

✔ Testeable

✔ Escalable

✔ Fácil de leer

✔ Fácil de mantener

---

# Flujo de Datos

```text
Usuario

↓

Widget

↓

Riverpod Provider

↓

Use Case

↓

Repository

↓

Remote Data Source

↓

API FastAPI

↓

PostgreSQL

↓

Respuesta

↓

Provider

↓

Widget

↓

UI Actualizada
```

---

# Principio Final

El Frontend de Together deberá ofrecer una experiencia fluida, elegante y consistente.

Cada pantalla deberá sentirse como parte de un mismo ecosistema visual, respetando el Design System y los principios de arquitectura definidos en los documentos anteriores.

El objetivo no es únicamente desarrollar una aplicación funcional, sino construir un producto con calidad comercial, preparado para escalar y ofrecer una experiencia de usuario comparable a aplicaciones premium como Revolut, Monzo o Apple Wallet.