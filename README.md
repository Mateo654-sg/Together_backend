<div align="center">

# Together — Backend

**API REST para la gestión inteligente de finanzas de pareja**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## Acerca de

**Together** es una aplicación móvil diseñada para parejas que desean gestionar sus finanzas de manera colaborativa e inteligente. Este repositorio contiene el **backend** de la aplicación, una API REST construida con FastAPI siguiendo los principios de **Clean Architecture** y **Repository Pattern**.

### Características principales

- Registro y autenticación segura (JWT + Argon2id)
- Gestión de finanzas personales y compartidas
- Metas y presupuestos financieros
- Asistente de IA para análisis financiero
- Chat integrado entre parejas
- Dashboard y reportes en tiempo real
- Sistema de notificaciones y recordatorios

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Framework** | FastAPI |
| **Lenguaje** | Python 3.12+ |
| **Base de datos** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2 (async) |
| **Migraciones** | Alembic |
| **Cache** | Redis 7 |
| **Auth** | JWT (Access 15min / Refresh 30d con rotación) |
| **Hashing** | Argon2id |
| **Validación** | Pydantic v2 |
| **Testing** | pytest + pytest-asyncio |
| **Linting** | Ruff |
| **Contenedorización** | Docker + Docker Compose |

---

## Arquitectura

Clean Architecture con Repository Pattern:

```
app/
├── api/v1/          # Routers (endpoints HTTP)
├── core/            # Configuración, seguridad, excepciones
├── db/              # Engine, session, base declarativa
├── models/          # Modelos ORM (SQLAlchemy)
├── schemas/         # Schemas Pydantic (request/response)
├── repositories/    # Capa de acceso a datos
├── use_cases/       # Lógica de negocio
├── services/        # Servicios externos (AI, etc.)
└── middlewares/      # Middlewares FastAPI
```

**Flujo de datos:**
```
Router → Use Case → Repository → Database
```

Los routers nunca acceden directamente a la base de datos. Toda la lógica de negocio vive en los Use Cases.

---

## Instalación

### Requisitos

- Python 3.12+
- PostgreSQL 16
- Redis 7
- Docker y Docker Compose (opcional)

### Setup Local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/together-backend.git
cd together-backend

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Crear base de datos
createdb together_db

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Setup con Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

Servicios levantados:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `backend` | 8000 | API FastAPI |
| `postgres` | 5432 | PostgreSQL 16 |
| `redis` | 6379 | Redis 7 |
| `pgadmin` | 5050 | Admin de PostgreSQL |

---

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `APP_ENV` | `development` | Entorno de ejecución |
| `DATABASE_URL` | `postgresql+asyncpg://...` | URL de conexión async |
| `DATABASE_URL_SYNC` | `postgresql+psycopg2://...` | URL de conexión sync (Alembic) |
| `REDIS_URL` | `redis://localhost:6379/0` | URL de Redis |
| `JWT_SECRET` | `CHANGE_ME` | Secreto para firmar JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de firmado |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Caducidad access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Caducidad refresh token |

Ver `.env.example` para la lista completa.

---

## Comandos Útiles

### Migraciones

```bash
# Crear migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

### Testing

```bash
# Crear base de datos de test
createdb together_test_db

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest tests/unit

# Solo tests de integración
pytest tests/integration
```

### Calidad de Código

```bash
# Verificar errores
python3 -m ruff check app/ tests/

# Auto-corregir
python3 -m ruff check app/ tests/ --fix

# Seguridad estática
bandit -r app/
```

---

## Módulos Implementados

| Módulo | Endpoints | Descripción |
|--------|-----------|-------------|
| **Auth** | 4 | Registro, login, refresh, logout |
| **Users** | 9 | Perfil, configuración, estadísticas, sesiones |
| **Couples** | 5 | Invitación, aceptar, rechazar, estado, desvincular |
| **Personal Finances** | 11 | Categorías, gastos e ingresos personales |
| **Shared Finances** | 9 | Gastos, ingresos y deudas compartidas |
| **Goals** | 7 | Metas financieras con contribuciones |
| **Budgets** | 5 | Presupuestos con alertas |
| **Dashboard** | 2 | Dashboard personal y de pareja |
| **Reports** | 6 | Generación y descarga de reportes |
| **Statistics** | 2 | Estadísticas mensuales y personales |
| **AI Assistant** | 14 | Chat, análisis, predicciones, simulador |
| **Reminders** | 5 | Recordatorios financieros |
| **Chat** | 3 | Mensajes entre parejas |
| **Notifications** | 4 | Notificaciones in-app |

**Total: 84 endpoints, 135 requerimientos funcionales**

---

## Estructura del Proyecto

```
together-backend/
├── alembic/              # Migraciones de base de datos
│   └── versions/         # 9 migraciones
├── app/
│   ├── api/v1/           # 18 routers
│   ├── core/             # Config, seguridad, excepciones
│   ├── db/               # Session y base
│   ├── models/           # 21 modelos ORM
│   ├── schemas/          # 14 schemas Pydantic
│   ├── repositories/     # 21 repositories
│   ├── use_cases/        # 12 dominios, ~65 use cases
│   └── services/ai/      # Servicio de IA
├── docs/                 # 17 documentos de especificación
├── tests/
│   ├── integration/      # 16 archivos de tests
│   └── unit/             # 2 archivos de tests
├── .env.example
├── docker-compose.dev.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Documentación

Los documentos de especificación del producto se encuentran en `/docs`:

| Documento | Contenido |
|-----------|-----------|
| `01-product-vision.md` | Visión del producto |
| `02-functional-requirements.md` | 135 requerimientos funcionales |
| `03-non-functional-requirements.md` | Requerimientos no funcionales |
| `06-system-architecture.md` | Arquitectura del sistema |
| `07-database-design.md` | Diseño de base de datos |
| `08-backend-api.md` | Especificación de la API |
| `10-ai-module.md` | Módulo de IA |
| `12-security.md` | Estrategia de seguridad |
| `13-testing.md` | Estrategia de testing |
| `15-roadmap.md` | Roadmap del producto |

Ver `docs/API.md` para la referencia completa de endpoints.

---

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para las guías de contribución.

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
