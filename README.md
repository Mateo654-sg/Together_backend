# 💕 Together — Backend

API REST de Together, construida con FastAPI siguiendo Clean Architecture.

Ver documentación completa del producto en la carpeta `/docs` del proyecto
(Documentos 01 al 17).

---

## Stack

- **Framework:** FastAPI
- **Lenguaje:** Python 3.12+
- **Base de datos:** PostgreSQL 16 (SQLAlchemy 2 async + Alembic)
- **Cache:** Redis
- **Auth:** JWT (Access 15 min / Refresh 30 días con rotación) + Argon2id

## Arquitectura

Clean Architecture con Repository Pattern y Use Cases:

```
app/
├── api/            # Routers + dependencias (Presentation)
├── core/           # Config, seguridad, excepciones
├── db/             # Engine, session, base declarativa
├── models/         # Modelos ORM (SQLAlchemy)
├── schemas/        # Pydantic (request/response)
├── repositories/   # Acceso a datos (Repository Pattern)
├── use_cases/      # Lógica de negocio (Application)
├── services/       # Servicios externos (futuro: email, S3, IA)
└── middlewares/
```

Flujo de dependencias:

```
Router → Use Case → Repository → Database
```

Nunca se accede a la base de datos directamente desde los routers.

## Setup local (sin Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env con tus credenciales de Postgres/Redis/JWT

# Crear base de datos
createdb together_db

# Aplicar migraciones
alembic upgrade head

# Levantar servidor
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.

Documentación interactiva: `http://localhost:8000/docs`

## Setup con Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

Levanta: `backend`, `postgres`, `redis`, `pgadmin` (puerto 5050).

## Migraciones

```bash
# Crear una nueva migración a partir de cambios en los modelos
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Revertir la última migración
alembic downgrade -1
```

## Testing

Requiere una base de datos `together_test_db` separada:

```bash
createdb together_test_db

pytest                                    # correr toda la suite
pytest --cov=app --cov-report=term-missing  # con cobertura
pytest tests/unit                         # solo unitarios
pytest tests/integration                  # solo integración
```

Cobertura mínima exigida: **90%** (Documento 13 — Testing Strategy).

## Calidad de código

```bash
ruff check app/          # Lint
ruff check app/ --fix    # Autofix
bandit -r app/           # Seguridad estática
```

## Endpoints implementados (Fase 1 — Auth & Users)

| Método | Endpoint | Descripción | FR |
|--------|----------|-------------|-----|
| POST | `/api/v1/auth/register` | Crear cuenta | FR-001 |
| POST | `/api/v1/auth/login` | Iniciar sesión | FR-002 |
| POST | `/api/v1/auth/refresh` | Renovar tokens (rotación) | — |
| POST | `/api/v1/auth/logout` | Cerrar sesión | FR-005 |
| POST | `/api/v1/auth/forgot-password` | Solicitar recuperación | FR-003 (pendiente) |
| POST | `/api/v1/auth/reset-password` | Restablecer contraseña | FR-003 (pendiente) |
| GET | `/api/v1/users/me` | Perfil del usuario autenticado | — |
| PUT | `/api/v1/users/me` | Editar perfil | FR-006 |
| DELETE | `/api/v1/users/me` | Eliminar cuenta (soft delete) | FR-010 |

## Próximos módulos (en orden sugerido)

1. **Pareja** (Couples): invitar, aceptar, desvincular (FR-011 a FR-018)
2. **Finanzas personales**: ingresos, gastos, categorías (FR-019 a FR-040)
3. **Finanzas compartidas**: gastos compartidos, deudas (FR-041 a FR-060)
4. **Metas**, **Presupuestos**, **Dashboard**...

Cada módulo nuevo debe seguir el mismo patrón: `models → schemas →
repositories → use_cases → api/v1/router → tests`.
