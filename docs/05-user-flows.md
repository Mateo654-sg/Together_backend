# 🔄 Together

# Documento 05 — User Flows

**Versión:** 1.0

**Estado:** Aprobado

---

# Objetivo

Este documento describe la experiencia completa del usuario dentro de Together.

Cada flujo representa una interacción importante con la aplicación y servirá como guía para el desarrollo del frontend, backend y las pruebas funcionales.

---

# Principios de UX

Todos los flujos deben cumplir los siguientes principios:

- Menor cantidad de pasos posible.
- Máximo 3 toques para registrar un gasto frecuente.
- Retroalimentación inmediata después de cada acción.
- Nunca dejar al usuario sin saber qué ocurrió.
- Confirmar únicamente acciones críticas.
- Priorizar la simplicidad sobre la cantidad de opciones.

---

# Flujo General del Usuario

```text
Abrir aplicación
        │
        ▼
 Splash Screen
        │
        ▼
¿Usuario autenticado?
        │
 ┌──────┴────────┐
 │               │
 No              Sí
 │               │
 ▼               ▼
 Login      Dashboard
 │
 ▼
 Vincular pareja (opcional)
 │
 ▼
 Dashboard
```

---

# Flujo 1 — Registro

## Objetivo

Permitir crear una cuenta nueva.

### Pasos

```
Splash

↓

Crear cuenta

↓

Nombre

↓

Correo

↓

Contraseña

↓

Confirmar contraseña

↓

Aceptar términos

↓

Crear cuenta

↓

Verificar correo

↓

Dashboard
```

---

### Validaciones

- Correo único.
- Contraseña segura.
- Nombre obligatorio.
- Verificación por correo.

---

### Resultado esperado

Usuario autenticado.

---

# Flujo 2 — Inicio de Sesión

```
Login

↓

Correo

↓

Contraseña

↓

Ingresar

↓

Dashboard
```

Alternativas

- Google
- Apple (iOS)

---

# Flujo 3 — Vincular Pareja

```
Perfil

↓

Invitar pareja

↓

Mostrar código

↓

Compartir

↓

La otra persona acepta

↓

Espacio compartido creado
```

---

### Resultado

Se habilitan:

- Gastos compartidos.
- Metas compartidas.
- Dashboard conjunto.
- IA compartida.

---

# Flujo 4 — Registrar Gasto Personal

```
Botón +

↓

Nuevo gasto

↓

Valor

↓

Categoría

↓

Descripción

↓

Guardar
```

Tiempo esperado

Menos de 15 segundos.

---

### Al guardar

Animación.

Vibración ligera.

Actualización inmediata del dashboard.

---

# Flujo 5 — Registrar Ingreso

```
+

↓

Ingreso

↓

Valor

↓

Categoría

↓

Guardar
```

Actualizar:

Saldo.

Flujo de caja.

Estadísticas.

---

# Flujo 6 — Registrar Gasto Compartido

```
+

↓

Gasto compartido

↓

Valor

↓

Categoría

↓

¿Quién pagó?

↓

¿Cómo dividir?

↓

Guardar
```

---

### División

50/50

Porcentaje

Monto fijo

Personalizada

---

### Resultado

Actualizar automáticamente:

- Balance compartido.
- Deudas.
- Dashboard.
- IA.

---

# Flujo 7 — Pagar una Deuda

```
Dashboard

↓

Detalle deuda

↓

Pagar con Nequi

↓

Abrir Nequi

↓

Enviar dinero

↓

Volver

↓

Confirmar pago

↓

Estado = Pagado
```

Importante:

Together nunca recibe dinero.

Solo registra el estado.

---

# Flujo 8 — Crear Meta

```
Metas

↓

Nueva Meta

↓

Nombre

↓

Imagen

↓

Monto objetivo

↓

Fecha

↓

Guardar
```

---

# Flujo 9 — Aportar a una Meta

```
Meta

↓

Agregar aporte

↓

Valor

↓

Guardar
```

Actualizar automáticamente

Barra de progreso.

Porcentaje.

Predicción.

---

# Flujo 10 — Crear Presupuesto

```
Presupuestos

↓

Nuevo presupuesto

↓

Categoría

↓

Monto

↓

Periodo

↓

Guardar
```

---

# Flujo 11 — Recordatorio

```
Recordatorios

↓

Nuevo

↓

Título

↓

Fecha

↓

Hora

↓

Repetición

↓

Guardar
```

---

# Flujo 12 — Consultar Dashboard

```
Inicio

↓

Resumen financiero

↓

Gráficas

↓

KPIs

↓

IA

↓

Actividad reciente
```

No requiere interacción adicional.

---

# Flujo 13 — Consultar Reportes

```
Reportes

↓

Seleccionar periodo

↓

Seleccionar filtros

↓

Visualizar

↓

Exportar
```

---

Formatos

PDF

Excel

CSV

---

# Flujo 14 — Consultar IA

```
IA

↓

Escribir pregunta

↓

Enviar

↓

Respuesta

↓

Acciones sugeridas
```

Ejemplos

¿Cuánto gastamos en comida?

¿Cuánto gasté solo yo?

¿Cuánto falta para el viaje?

---

# Flujo 15 — Editar Perfil

```
Perfil

↓

Editar

↓

Guardar
```

---

# Flujo 16 — Cambiar Tema

```
Configuración

↓

Tema

↓

Claro

Oscuro

Sistema
```

---

# Flujo 17 — Notificación

```
Push

↓

Abrir

↓

Detalle

↓

Acción
```

Ejemplo

"Tu pareja registró un nuevo gasto."

---

# Flujo 18 — Cerrar Sesión

```
Perfil

↓

Cerrar sesión

↓

Confirmar

↓

Login
```

---

# Flujo 19 — Eliminar Cuenta

```
Configuración

↓

Eliminar cuenta

↓

Confirmar contraseña

↓

Confirmación

↓

Eliminar
```

---

# Flujo 20 — Estado Vacío

Cuando no existan datos, la aplicación nunca mostrará pantallas vacías.

Ejemplos

## Sin gastos

"Comienza registrando tu primer gasto 💸"

Botón

Registrar gasto

---

## Sin pareja

"Invita a tu pareja para comenzar a construir metas juntos ❤️"

Botón

Invitar

---

## Sin metas

"Todo gran sueño comienza con una meta."

Botón

Crear Meta

---

# Flujo de Errores

La aplicación nunca mostrará errores técnicos al usuario.

Incorrecto

```
500 Internal Server Error
```

Correcto

```
Parece que ocurrió un problema.

Intentemos nuevamente.
```

---

# Confirmaciones

Solicitar confirmación únicamente para:

- Eliminar movimiento.
- Eliminar meta.
- Eliminar cuenta.
- Desvincular pareja.

Nunca para registrar movimientos.

---

# Principios de Navegación

La navegación será consistente en toda la aplicación.

Bottom Navigation

- Inicio
- Actividad
- Metas
- IA
- Perfil

Botón flotante

Registrar movimiento.

---

# Tiempo Máximo por Flujo

| Flujo | Tiempo esperado |
|---------|----------------|
| Registrar gasto | < 15 s |
| Registrar ingreso | < 15 s |
| Crear meta | < 30 s |
| Consultar dashboard | < 2 s |
| Consultar IA | < 5 s |
| Crear presupuesto | < 20 s |
| Vincular pareja | < 2 min |

---

# Conclusión

Todos los flujos definidos en este documento representan el comportamiento esperado del usuario dentro de Together.

Cualquier nueva funcionalidad deberá integrarse respetando estos principios:

- Simplicidad.
- Rapidez.
- Elegancia.
- Consistencia.
- Experiencia Premium.
- Diseño centrado en el usuario.