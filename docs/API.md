# API Reference — Together Backend v1

Base URL: `http://localhost:8000/api/v1`

---

## Autenticación

Todos los endpoints (excepto register y login) requieren header:
```
Authorization: Bearer <access_token>
```

### Obtener Token

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/register` | POST | Registrar usuario |
| `/auth/login` | POST | Login (retorna access + refresh tokens) |
| `/auth/refresh` | POST | Renovar access token |
| `/auth/logout` | POST | Cerrar sesión (revoca refresh token) |

---

## Usuarios

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/users/me` | GET | Consultar perfil |
| `/users/me` | PUT | Editar perfil |
| `/users/me` | DELETE | Eliminar cuenta |
| `/users/change-password` | POST | Cambiar contraseña |
| `/users/sessions` | GET | Historial de sesiones |
| `/users/settings` | GET | Consultar configuración |
| `/users/settings` | PUT | Actualizar configuración |
| `/users/avatar` | PATCH | Actualizar avatar |
| `/users/statistics` | GET | Estadísticas personales |

---

## Parejas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/couples/invite` | POST | Crear invitación |
| `/couples/accept` | POST | Aceptar invitación |
| `/couples/reject` | POST | Rechazar invitación |
| `/couples/status` | GET | Estado de la pareja |
| `/couples/unlink` | POST | Desvincular pareja |

---

## Finanzas Personales

### Categorías

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/categories` | GET | Listar categorías |
| `/categories` | POST | Crear categoría |
| `/categories/{id}` | GET | Consultar categoría |
| `/categories/{id}` | PUT | Actualizar categoría |
| `/categories/{id}` | DELETE | Eliminar categoría |

### Gastos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/expenses` | GET | Listar gastos |
| `/expenses` | POST | Crear gasto |
| `/expenses/{id}` | GET | Consultar gasto |
| `/expenses/{id}` | PUT | Actualizar gasto |
| `/expenses/{id}` | DELETE | Eliminar gasto |

### Ingresos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/incomes` | GET | Listar ingresos |
| `/incomes` | POST | Crear ingreso |
| `/incomes/{id}` | GET | Consultar ingreso |
| `/incomes/{id}` | PUT | Actualizar ingreso |
| `/incomes/{id}` | DELETE | Eliminar ingreso |

### Balance

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/expenses/balance` | GET | Balance financiero personal |

---

## Finanzas Compartidas

### Gastos Compartidos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/shared-expenses` | GET | Listar gastos compartidos |
| `/shared-expenses` | POST | Crear gasto compartido |
| `/shared-expenses/{id}` | PUT | Actualizar gasto compartido |
| `/shared-expenses/{id}` | DELETE | Eliminar gasto compartido |

### Ingresos Compartidos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/shared-incomes` | GET | Listar ingresos compartidos |
| `/shared-incomes` | POST | Crear ingreso compartido |

### Deudas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/debts` | GET | Listar deudas |
| `/debts/{id}/pay` | POST | Pagar deuda |
| `/debts/history` | GET | Historial de deudas |

---

## Metas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/goals` | GET | Listar metas |
| `/goals` | POST | Crear meta |
| `/goals/{id}` | PUT | Actualizar meta |
| `/goals/{id}` | DELETE | Eliminar meta |
| `/goals/{id}/contribute` | POST | Contribuir a meta |
| `/goals/{id}/history` | GET | Historial de contribuciones |
| `/goals/statistics` | GET | Estadísticas de metas |

---

## Presupuestos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/budgets` | GET | Listar presupuestos |
| `/budgets` | POST | Crear presupuesto |
| `/budgets/{id}` | PUT | Actualizar presupuesto |
| `/budgets/{id}` | DELETE | Eliminar presupuesto |
| `/budgets/alerts` | GET | Alertas de presupuesto |

---

## Dashboard

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/dashboard` | GET | Dashboard personal |
| `/dashboard/couple` | GET | Dashboard de pareja |

---

## Reportes y Estadísticas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/reports` | POST | Generar reporte |
| `/reports` | GET | Listar reportes |
| `/reports/{id}` | GET | Descargar reporte |
| `/reports/{id}` | DELETE | Eliminar reporte |
| `/statistics/monthly` | GET | Estadísticas mensuales |
| `/statistics/personal` | GET | Estadísticas personales |

---

## Asistente IA

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/ai/chat` | POST | Chat con asistente |
| `/ai/analyze` | POST | Análisis de gastos |
| `/ai/predictions` | POST | Predicciones financieras |
| `/ai/score` | POST | Score de salud financiera |
| `/ai/insights` | POST | Insights financieros |
| `/ai/recommendations` | POST | Recomendaciones |
| `/ai/summary` | POST | Resumen financiero |
| `/ai/financial-health` | POST | Salud financiera |
| `/ai/simulator` | POST | Simulador financiero |
| `/ai/history` | GET | Historial de interacciones |

---

## Recordatorios

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/reminders` | GET | Listar recordatorios |
| `/reminders` | POST | Crear recordatorio |
| `/reminders/{id}` | PUT | Actualizar recordatorio |
| `/reminders/{id}` | DELETE | Eliminar recordatorio |
| `/reminders/{id}/complete` | PATCH | Marcar como completado |

---

## Chat

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/chat` | GET | Listar mensajes |
| `/chat` | POST | Enviar mensaje |
| `/chat/{id}` | DELETE | Eliminar mensaje |

---

## Notificaciones

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/notifications` | GET | Listar notificaciones |
| `/notifications/{id}/read` | PATCH | Marcar como leída |
| `/notifications/read` | PATCH | Marcar todas como leídas |
| `/notifications/{id}` | DELETE | Eliminar notificación |

---

## Formato de Errores

```json
{
  "success": false,
  "message": "Descripción del error",
  "errors": []
}
```

### Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## Paginación

Endpoints de listado retornan:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5
  }
}
```
