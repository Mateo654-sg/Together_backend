# Contribuir a Together Backend

Gracias por tu interés en contribuir a Together. Este documento expone las convenciones y el flujo de trabajo para mantener la calidad del código.

---

## Requisitos Previos

- Python 3.12+
- PostgreSQL 16
- Redis 7
- Docker y Docker Compose (opcional pero recomendado)

---

## Configuración del Entorno

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
# Editar .env con tus valores

# Crear base de datos
createdb together_db

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

Con Docker:
```bash
docker compose -f docker-compose.dev.yml up --build
```

---

## Arquitectura del Proyecto

```
app/
├── api/v1/          # Routers (endpoints HTTP)
├── core/            # Configuración, seguridad, excepciones
├── db/              # Sesión y base de base
├── models/          # Modelos ORM (SQLAlchemy)
├── schemas/         # Schemas Pydantic (request/response)
├── repositories/    # Capa de acceso a datos
├── use_cases/       # Lógica de negocio
├── services/        # Servicios externos (AI, email, etc.)
└── middlewares/      # Middlewares FastAPI
```

**Flujo de datos:**
```
Router → Use Case → Repository → Database
```

---

## Convenciones de Código

### Formateo y Lint

```bash
# Verificar errores
python3 -m ruff check app/ tests/

# Auto-corregir
python3 -m ruff check app/ tests/ --fix
```

### Reglas

- **Sin comentarios** a menos que se soliciten explícitamente
- **Clean Architecture**: los routers no contienen lógica de negocio
- **UUID** como primary key en todas las tablas
- **Soft Delete** (`deleted_at`) en todas las tablas
- **Timestamps**: `created_at` y `updated_at` en todas las tablas
- **Error format**: `{"success": false, "message": "...", "errors": []}`

### Commits

Usar convención de commits:
```
feat: add new endpoint for goal creation
fix: resolve authentication token refresh issue
docs: update API documentation
refactor: extract use case logic from router
test: add integration tests for chat module
```

---

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Ver reporte
open htmlcov/index.html
```

### Requisitos

- **Cobertura mínima**: 90%
- **Tests de integración** para cada endpoint
- **Tests unitarios** para lógica de negocio crítica

---

## Flujo de Trabajo

1. Crear una rama desde `main`:
   ```bash
   git checkout -b feat/nombre-del-feature
   ```

2. Hacer cambios y verificar lint:
   ```bash
   python3 -m ruff check app/ tests/
   ```

3. Ejecutar tests:
   ```bash
   pytest
   ```

4. Crear commit con mensaje descriptivo:
   ```bash
   git commit -m "feat: add budget alerts endpoint"
   ```

5. Push y crear Pull Request:
   ```bash
   git push origin feat/nombre-del-feature
   ```

---

## Estructura de un Módulo Nuevo

Para agregar un módulo nuevo:

1. **Modelo**: `app/models/nuevo_modulo.py`
2. **Schema**: `app/schemas/nuevo_modulo.py`
3. **Repository**: `app/repositories/nuevo_modulo_repository.py`
4. **Use Cases**: `app/use_cases/nuevo_modulo/`
5. **Router**: `app/api/v1/nuevo_modulo.py`
6. **Migración**: `alembic revision --autogenerate -m "add nuevo_modulo table"`
7. **Tests**: `tests/integration/test_nuevo_modulo_endpoints.py`
8. **Registrar** router en `app/api/v1/__init__.py`
9. **Registrar** modelo en `app/models/__init__.py`

---

## Preguntas

Si tienes dudas, abre un issue en el repositorio.
