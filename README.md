# Together Backend

API REST para la aplicacion de gestion de finanzas compartidas en parejas.

## Stack

| Componente         | Tecnologia                     |
| ------------------ | ------------------------------ |
| Runtime            | Python 3.12+                   |
| Framework          | FastAPI 0.115                  |
| ORM                | SQLAlchemy 2.0.35 (async)      |
| Migraciones        | Alembic 1.13                   |
| Base de datos      | PostgreSQL 16                  |
| Cache              | Redis 7                        |
| Autenticacion      | JWT (python-jose) + Argon2id   |
| Validacion         | Pydantic 2.9                   |
| Testing            | Pytest + pytest-asyncio        |
| Linting            | Ruff + Bandit                  |
| Contenedores       | Docker (multi-stage build)     |

## Requisitos previos

- Python 3.12 o superior
- PostgreSQL 16
- Redis 7
- pip

## Instalacion

### Clonar el repositorio

```bash
git clone <repo-url>
cd together-backend
```

### Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### Configurar base de datos

```bash
# Crear la base de datos en PostgreSQL
createdb together_db

# Ejecutar migraciones con Alembic
alembic upgrade head
```

### Ejecutar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estara disponible en:

- Servidor: `http://localhost:8000`
- Documentacion Swagger: `http://localhost:8000/docs`
- Documentacion ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Variables de entorno

Todas las variables se cargan desde el archivo `.env` usando `pydantic-settings`.

| Variable                       | Requerida | Valor por defecto                      | Descripcion                                             |
| ------------------------------ | --------- | -------------------------------------- | ------------------------------------------------------- |
| `APP_ENV`                      | No        | `development`                          | Entorno de ejecucion (`development`, `production`, `testing`) |
| `APP_NAME`                     | No        | `Together API`                         | Nombre de la API (titulo de Swagger)                    |
| `APP_VERSION`                  | No        | `v1`                                   | Version actual de la API                                |
| `DEBUG`                        | No        | `true`                                 | Habilita modo debug (SQLAlchemy echo, logs)             |
| `DATABASE_URL`                 | Si        | -                                      | URL de conexion async a PostgreSQL (asyncpg)            |
| `DATABASE_URL_SYNC`            | Si        | -                                      | URL de conexion sync para Alembic (psycopg2)            |
| `REDIS_URL`                    | No        | `redis://localhost:6379/0`             | URL de conexion a Redis                                 |
| `JWT_SECRET`                   | Si        | -                                      | Secreto para firmar tokens JWT                          |
| `JWT_ALGORITHM`                | No        | `HS256`                                | Algoritmo de firmado JWT                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | No        | `15`                                   | Minutos de vida del access token                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`    | No        | `30`                                   | Dias de vida del refresh token                          |
| `CORS_ORIGINS`                 | No        | `["http://localhost:3000"]`            | Origenes permitidos para CORS (formato JSON array)      |
| `OPENAI_API_KEY`               | No        | -                                      | API Key de OpenAI (modulo de IA, futuro)                |
| `AWS_ACCESS_KEY_ID`            | No        | -                                      | ID de acceso AWS (futuro)                               |
| `AWS_SECRET_ACCESS_KEY`        | No        | -                                      | Secreto de acceso AWS (futuro)                          |
| `S3_BUCKET`                    | No        | -                                      | Nombre del bucket S3 (futuro)                           |

## Estructura del proyecto

```
together-backend/
├── app/
│   ├── api/
│   │   ├── deps.py                  # Dependencias FastAPI (auth, IP, device)
│   │   └── v1/
│   │       ├── __init__.py          # Registro del APIRouter principal (prefijo /api/v1)
│   │       ├── ai.py                # Endpoints del asistente financiero IA
│   │       ├── auth.py              # Registro, login, refresh, logout
│   │       ├── budgets.py           # CRUD de presupuestos
│   │       ├── categories.py        # CRUD de categorias personales
│   │       ├── chat.py              # Chat de pareja
│   │       ├── couples.py           # Vinculacion de pareja
│   │       ├── dashboard.py         # Dashboard personal y de pareja
│   │       ├── debts.py             # Deudas y balance de pareja
│   │       ├── expenses.py          # CRUD de gastos personales
│   │       ├── goals.py             # Metas compartidas y aportes
│   │       ├── incomes.py           # CRUD de ingresos personales
│   │       ├── notifications.py     # Notificaciones
│   │       ├── reminders.py         # Recordatorios financieros
│   │       ├── reports.py           # Generacion y descarga de reportes
│   │       ├── shared_expenses.py   # CRUD de gastos compartidos
│   │       ├── shared_incomes.py    # CRUD de ingresos compartidos
│   │       ├── statistics.py        # Estadisticas financieras
│   │       └── users.py             # Perfil, configuracion, sesiones
│   ├── core/
│   │   ├── config.py                # Configuracion central (pydantic-settings)
│   │   ├── exceptions.py            # Excepciones personalizadas de la aplicacion
│   │   └── security.py              # JWT (access/refresh) y hashing Argon2id
│   ├── db/
│   │   ├── base.py                  # Base declarativa, UUIDMixin, TimestampMixin
│   │   └── session.py               # Engine async y get_db dependency
│   ├── models/                      # Modelos ORM (18 modelos)
│   │   ├── ai_history.py
│   │   ├── budget.py
│   │   ├── chat_message.py
│   │   ├── couple.py
│   │   ├── debt.py
│   │   ├── goal.py
│   │   ├── goal_contribution.py
│   │   ├── login_history.py
│   │   ├── notification.py
│   │   ├── personal_category.py
│   │   ├── personal_expense.py
│   │   ├── personal_income.py
│   │   ├── reminder.py
│   │   ├── report.py
│   │   ├── session.py
│   │   ├── shared_category.py
│   │   ├── shared_expense.py
│   │   ├── shared_income.py
│   │   ├── user.py
│   │   └── user_settings.py
│   ├── repositories/                # Capa de acceso a datos (Repository Pattern)
│   │   ├── base_repository.py
│   │   ├── ai_history_repository.py
│   │   ├── budget_repository.py
│   │   ├── chat_repository.py
│   │   ├── couple_repository.py
│   │   ├── debt_repository.py
│   │   ├── goal_contribution_repository.py
│   │   ├── goal_repository.py
│   │   ├── login_history_repository.py
│   │   ├── notification_repository.py
│   │   ├── personal_category_repository.py
│   │   ├── personal_expense_repository.py
│   │   ├── personal_income_repository.py
│   │   ├── reminder_repository.py
│   │   ├── report_repository.py
│   │   ├── session_repository.py
│   │   ├── shared_category_repository.py
│   │   ├── shared_expense_repository.py
│   │   ├── shared_income_repository.py
│   │   └── user_repository.py
│   ├── schemas/                     # Schemas Pydantic (request/response)
│   │   ├── ai.py
│   │   ├── auth.py
│   │   ├── budget.py
│   │   ├── chat.py
│   │   ├── couple.py
│   │   ├── dashboard.py
│   │   ├── goal.py
│   │   ├── notification.py
│   │   ├── personal_finance.py
│   │   ├── reminder.py
│   │   ├── report.py
│   │   ├── shared_finance.py
│   │   └── user.py
│   ├── services/
│   │   └── ai/                      # Servicio de IA (mock provider + context builder)
│   │       ├── base.py
│   │       ├── context_builder.py
│   │       ├── mock_provider.py
│   │       └── service.py
│   ├── use_cases/                   # Logica de negocio (Clean Architecture)
│   │   ├── ai/                      # 9 casos de uso de IA
│   │   ├── auth/                    # 4 casos de uso de autenticacion
│   │   ├── budgets/                 # 5 casos de uso de presupuestos
│   │   ├── chat/                    # 3 casos de uso de chat
│   │   ├── couples/                 # 5 casos de uso de pareja
│   │   ├── dashboard/               # 2 casos de uso de dashboard
│   │   ├── goals/                   # 7 casos de uso de metas
│   │   ├── notifications/           # 4 casos de uso de notificaciones
│   │   ├── personal_finance/        # 15 casos de uso de finanzas personales
│   │   ├── reminders/               # 5 casos de uso de recordatorios
│   │   ├── reports/                 # 6 casos de uso de reportes
│   │   ├── shared_finance/          # 10 casos de uso de finanzas compartidas
│   │   └── users/                   # 7 casos de uso de usuarios
│   ├── utils/
│   │   └── codes.py                 # Generacion de codigos de invitacion
│   └── main.py                      # Punto de entrada FastAPI
├── alembic/                         # Migraciones de base de datos
│   ├── env.py
│   └── versions/                    # 9 migraciones
├── tests/
│   ├── conftest.py
│   ├── unit/                        # Tests unitarios
│   └── integration/                 # Tests de integracion (14 archivos)
├── alembic.ini                      # Configuracion de Alembic
├── Dockerfile                       # Build multi-stage (Python 3.12-slim)
├── docker-compose.dev.yml           # Postgres + Redis + Backend + PgAdmin
├── requirements.txt                 # Dependencias de Python
├── pytest.ini                       # Configuracion de Pytest
├── .env.example                     # Plantilla de variables de entorno
├── .coveragerc                      # Configuracion de coverage
├── CHANGELOG.md                     # Historial de cambios
├── CONTRIBUTING.md                   # Guia de contribucion
└── LICENSE                          # MIT License
```

**Total de archivos Python:** 221 (incluyendo tests y migraciones)

## Endpoints API

Toda la API se encuentra bajo el prefijo `/api/v1`. La API expose **90 endpoints** mas el endpoint de health check.

### Health Check

| Metodo | Endpoint    | Descripcion                     | Auth |
| ------ | ----------- | ------------------------------- | ---- |
| GET    | `/health`   | Verificacion de estado del API  | No   |

### Auth - `/api/v1/auth`

| Metodo | Endpoint                   | Descripcion                                     | Auth |
| ------ | -------------------------- | ----------------------------------------------- | ---- |
| POST   | `/register`                | Crear una cuenta nueva                          | No   |
| POST   | `/login`                   | Iniciar sesion (retorna access + refresh token)  | No   |
| POST   | `/refresh`                 | Renovar access token via rotacion de refresh    | No   |
| POST   | `/logout`                  | Cerrar sesion (invalida refresh token)          | Si   |
| POST   | `/forgot-password`         | Solicitar recuperacion de contrasena            | No   |
| POST   | `/reset-password`          | Restablecer contrasena con token                | No   |

### Users - `/api/v1/users`

| Metodo | Endpoint          | Descripcion                              | Auth |
| ------ | ----------------- | ---------------------------------------- | ---- |
| GET    | `/me`             | Obtener perfil del usuario actual        | Si   |
| PUT    | `/me`             | Actualizar perfil del usuario            | Si   |
| DELETE | `/me`             | Eliminar cuenta (requiere contrasena)    | Si   |
| GET    | `/settings`       | Obtener configuracion del usuario        | Si   |
| PUT    | `/settings`       | Actualizar configuracion del usuario     | Si   |
| PATCH  | `/avatar`         | Actualizar foto de perfil                | Si   |
| GET    | `/statistics`     | Estadisticas personales del usuario      | Si   |
| POST   | `/change-password`| Cambiar contrasena                       | Si   |
| GET    | `/sessions`       | Historial de sesiones activas            | Si   |

### Couples - `/api/v1/couples`

| Metodo | Endpoint     | Descripcion                              | Auth |
| ------ | ------------ | ---------------------------------------- | ---- |
| GET    | `/`          | Estado de la relacion (sin pareja/pendiente/vinculada) | Si   |
| POST   | `/invite`    | Generar codigo de invitacion             | Si   |
| POST   | `/accept`    | Aceptar invitacion por codigo            | Si   |
| POST   | `/reject`    | Rechazar invitacion por codigo           | Si   |
| DELETE | `/unlink`    | Desvincular pareja                       | Si   |

### Personal Expenses - `/api/v1/expenses`

| Metodo | Endpoint           | Descripcion                              | Auth |
| ------ | ------------------ | ---------------------------------------- | ---- |
| GET    | `/balance`         | Saldo personal (ingresos - gastos)       | Si   |
| GET    | `/`                | Listar gastos (filtros, busqueda, paginacion) | Si   |
| GET    | `/{expense_id}`    | Obtener un gasto por ID                  | Si   |
| POST   | `/`                | Registrar un gasto nuevo                 | Si   |
| PUT    | `/{expense_id}`    | Editar un gasto existente                | Si   |
| DELETE | `/{expense_id}`    | Eliminar un gasto (soft delete)          | Si   |
| POST   | `/duplicate`       | Duplicar un gasto existente              | Si   |

### Personal Incomes - `/api/v1/incomes`

| Metodo | Endpoint          | Descripcion                              | Auth |
| ------ | ----------------- | ---------------------------------------- | ---- |
| GET    | `/`               | Listar ingresos (filtros, paginacion)    | Si   |
| POST   | `/`               | Registrar un ingreso nuevo               | Si   |
| PUT    | `/{income_id}`    | Editar un ingreso existente              | Si   |
| DELETE | `/{income_id}`    | Eliminar un ingreso (soft delete)        | Si   |

### Shared Expenses - `/api/v1/shared-expenses`

| Metodo | Endpoint           | Descripcion                              | Auth |
| ------ | ------------------ | ---------------------------------------- | ---- |
| GET    | `/`                | Listar gastos compartidos (filtros)      | Si   |
| POST   | `/`                | Registrar gasto compartido (division automatica) | Si   |
| PUT    | `/{expense_id}`    | Editar gasto compartido                  | Si   |
| DELETE | `/{expense_id}`    | Eliminar gasto compartido                | Si   |

### Shared Incomes - `/api/v1/shared-incomes`

| Metodo | Endpoint    | Descripcion                              | Auth |
| ------ | ----------- | ---------------------------------------- | ---- |
| GET    | `/`         | Listar ingresos compartidos              | Si   |
| POST   | `/`         | Registrar ingreso compartido             | Si   |

### Goals - `/api/v1/goals`

| Metodo | Endpoint           | Descripcion                              | Auth |
| ------ | ------------------ | ---------------------------------------- | ---- |
| GET    | `/`                | Listar metas de la pareja (filtros)      | Si   |
| POST   | `/`                | Crear una nueva meta compartida          | Si   |
| PUT    | `/{goal_id}`       | Editar una meta existente                | Si   |
| DELETE | `/{goal_id}`       | Eliminar una meta (soft delete)          | Si   |
| POST   | `/contribute`      | Registrar un aporte a una meta           | Si   |
| GET    | `/history`         | Historial de aportes a metas             | Si   |
| GET    | `/statistics`      | Estadisticas generales de metas          | Si   |

### Budgets - `/api/v1/budgets`

| Metodo | Endpoint     | Descripcion                              | Auth |
| ------ | ------------ | ---------------------------------------- | ---- |
| GET    | `/`          | Listar presupuestos (filtros, paginacion)| Si   |
| POST   | `/`          | Crear un nuevo presupuesto               | Si   |
| PUT    | `/{budget_id}` | Editar un presupuesto existente        | Si   |
| DELETE | `/{budget_id}` | Eliminar un presupuesto (soft delete)  | Si   |
| GET    | `/alerts`    | Alertas de presupuestos (80%, 90%, 100%)| Si   |

### Debts - `/api/v1/debts`

| Metodo | Endpoint           | Descripcion                              | Auth |
| ------ | ------------------ | ---------------------------------------- | ---- |
| GET    | `/`                | Listar deudas pendientes                 | Si   |
| GET    | `/history`         | Historial completo de deudas             | Si   |
| POST   | `/{debt_id}/pay`   | Marcar deuda como pagada                 | Si   |
| GET    | `/balance`         | Balance financiero de la pareja          | Si   |

### Notifications - `/api/v1/notifications`

| Metodo | Endpoint                    | Descripcion                              | Auth |
| ------ | --------------------------- | ---------------------------------------- | ---- |
| GET    | `/`                         | Listar notificaciones (filtro no leidas) | Si   |
| PATCH  | `/read`                     | Marcar todas como leidas                 | Si   |
| PATCH  | `/{notification_id}/read`   | Marcar una como leida                    | Si   |
| DELETE | `/{notification_id}`        | Eliminar notificacion (soft delete)      | Si   |

### Reminders - `/api/v1/reminders`

| Metodo | Endpoint                       | Descripcion                              | Auth |
| ------ | ------------------------------ | ---------------------------------------- | ---- |
| GET    | `/`                            | Listar recordatorios (filtros)           | Si   |
| POST   | `/`                            | Crear un recordatorio nuevo              | Si   |
| PUT    | `/{reminder_id}`               | Editar un recordatorio existente         | Si   |
| DELETE | `/{reminder_id}`               | Eliminar un recordatorio (soft delete)   | Si   |
| PATCH  | `/{reminder_id}/complete`      | Marcar recordatorio como completado      | Si   |

### Dashboard - `/api/v1/dashboard`

| Metodo | Endpoint   | Descripcion                              | Auth |
| ------ | ---------- | ---------------------------------------- | ---- |
| GET    | `/`        | Dashboard principal con resumen de finanzas | Si  |
| GET    | `/couple`  | Dashboard de pareja con datos compartidos| Si   |

### Statistics - `/api/v1/statistics`

| Metodo | Endpoint     | Descripcion                              | Auth |
| ------ | ------------ | ---------------------------------------- | ---- |
| GET    | `/month`     | Estadisticas del mes                     | Si   |
| GET    | `/personal`  | Estadisticas personales                  | Si   |

### Reports - `/api/v1/reports`

| Metodo | Endpoint           | Descripcion                              | Auth |
| ------ | ------------------ | ---------------------------------------- | ---- |
| GET    | `/`                | Listar reportes generados                | Si   |
| POST   | `/`                | Generar un nuevo reporte                 | Si   |
| GET    | `/{report_id}`     | Obtener info de un reporte para descarga | Si   |
| DELETE | `/{report_id}`     | Eliminar un reporte (soft delete)        | Si   |

### AI - `/api/v1/ai`

| Metodo | Endpoint                  | Descripcion                              | Auth |
| ------ | ------------------------- | ---------------------------------------- | ---- |
| POST   | `/chat`                   | Chat en lenguaje natural                 | Si   |
| POST   | `/analyze`                | Detectar patrones, anomalias, comparar periodos | Si   |
| POST   | `/predictions`            | Predicciones de ahorro y metas           | Si   |
| GET    | `/insights`               | Insights automaticos                     | Si   |
| POST   | `/score`                  | Calcular Score Financiero                | Si   |
| POST   | `/recommendations`        | Recomendaciones personalizadas           | Si   |
| POST   | `/monthly-summary`        | Resumen mensual                          | Si   |
| POST   | `/weekly-summary`         | Resumen semanal                          | Si   |
| POST   | `/financial-health`       | Evaluar salud financiera                 | Si   |
| POST   | `/simulate`               | Simular escenarios financieros           | Si   |
| GET    | `/history`                | Historial de interacciones con IA        | Si   |
| DELETE | `/history/{history_id}`   | Eliminar interaccion del historial       | Si   |
| POST   | `/feedback`               | Enviar feedback sobre respuesta de IA    | Si   |

### Chat - `/api/v1/chat`

| Metodo | Endpoint               | Descripcion                              | Auth |
| ------ | ---------------------- | ---------------------------------------- | ---- |
| GET    | `/`                    | Listar mensajes del chat con la pareja   | Si   |
| POST   | `/`                    | Enviar un mensaje                        | Si   |
| DELETE | `/{message_id}`        | Eliminar un mensaje                      | Si   |

### Categories - `/api/v1/categories`

| Metodo | Endpoint             | Descripcion                              | Auth |
| ------ | -------------------- | ---------------------------------------- | ---- |
| GET    | `/`                  | Listar categorias personales             | Si   |
| POST   | `/`                  | Crear una categoria nueva                | Si   |
| PUT    | `/{category_id}`     | Actualizar una categoria                 | Si   |
| DELETE | `/{category_id}`     | Eliminar una categoria (soft delete)     | Si   |

## Arquitectura

El proyecto sigue un patron de **Clean Architecture** con las siguientes capas:

- **API (Routers):** Validan el request via Pydantic y delegan al caso de uso correspondiente.
- **Use Cases:** Contienen toda la logica de negocio. Cada operacion tiene su propio caso de uso.
- **Repositories:** Capa de acceso a datos que abstrae SQLAlchemy. Nunca se accede a la BD desde los routers.
- **Models:** Modelos ORM con UUID como PK, timestamps de auditoria y soft delete en todas las tablas.
- **Schemas:** Schemas Pydantic para validacion de request y serializacion de response.

### Convenciones de base de datos

- Todas las tablas usan **UUID v4** como llave primaria.
- Todas las tablas tienen `created_at`, `updated_at` y `deleted_at` (soft delete).
- Nunca se realiza `DELETE` fisico: solo se marca `deleted_at`.

## Autenticacion

La autenticacion utiliza **JWT (JSON Web Tokens)** con dos tipos de token:

1. **Access Token:** Corta duracion (15 minutos por defecto). Se envia en el header `Authorization: Bearer <token>`.
2. **Refresh Token:** Larga duracion (30 dias por defecto). Se usa para renovar el access token sin relogin.

### Flujo de autenticacion

1. El usuario envia credenciales a `POST /api/v1/auth/login`.
2. El servidor retorna `access_token` y `refresh_token`.
3. El cliente envia el `access_token` en el header `Authorization: Bearer <token>` en cada request autenticado.
4. Cuando el access token expira, el cliente envia el `refresh_token` a `POST /api/v1/auth/refresh` para obtener uno nuevo.
5. El refresh token se rotaciona: al usarse, el anterior queda invalidado.

### Seguridad

- Contrasenas se hashean con **Argon2id** (memory_cost: 64MB, iterations: 4, parallelism: 2).
- Cada token tiene un `jti` (JWT ID) unico para permitir invalidacion especifica.
- Los endpoints protegidos usan la dependencia `get_current_user` que valida el token y carga el usuario desde la BD.

## Despliegue con Docker

### Desarrollo

```bash
# Levantar servicios (PostgreSQL + Redis + Backend + PgAdmin)
docker compose -f docker-compose.dev.yml up -d

# Ver logs del backend
docker compose -f docker-compose.dev.yml logs -f backend
```

Los servicios estaran disponibles en:

| Servicio  | Puerto |
| --------- | ------ |
| Backend   | 8000   |
| PostgreSQL| 5432   |
| Redis     | 6379   |
| PgAdmin   | 5050   |

Credenciales de PgAdmin: `admin@together.app` / `admin`

### Produccion

El `Dockerfile` implementa un build multi-stage optimizado:

1. **Builder:** Instala dependencias en `/root/.local`.
2. **Runtime:** Imagen ligera con solo las dependencias de ejecucion, usuario no-root (`appuser`), y healthcheck configurado.

```bash
# Construir imagen
docker build -t together-backend .

# Ejecutar
docker run -p 8000:8000 --env-file .env together-backend
```

El healthcheck verifica el endpoint `/health` cada 30 segundos.

## Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con coverage
coverage run -m pytest
coverage report

# Ejecutar solo tests unitarios
pytest tests/unit/

# Ejecutar tests de integracion
pytest tests/integration/
```

Los tests usan `pytest-asyncio` con modo `auto` para testing asincrono.

## Linting y calidad

```bash
# Linting con Ruff
ruff check app/ tests/

# Analisis de seguridad con Bandit
bandit -r app/
```

## Licencia

MIT License - Copyright (c) 2026 Together
