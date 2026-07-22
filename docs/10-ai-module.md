# 🤖 Together

# Documento 10 — AI Module

**Versión:** 1.0

**Estado:** Aprobado

**Módulo:** Artificial Intelligence

---

# Objetivo

El módulo de Inteligencia Artificial de Together tiene como propósito transformar los datos financieros de los usuarios en información útil, recomendaciones accionables y predicciones que ayuden a tomar mejores decisiones financieras.

La IA no reemplaza al usuario.

La IA actúa como un **Asistente Financiero Inteligente**.

---

# Filosofía

La IA debe:

- Explicar.
- Recomendar.
- Enseñar.
- Motivar.
- Detectar riesgos.
- Detectar oportunidades.

Nunca deberá tomar decisiones por el usuario.

---

# Principios

La IA debe ser:

- Transparente
- Explicable
- Personalizada
- Segura
- Rápida
- Escalable

---

# Arquitectura General

```text
Usuario

↓

Pregunta

↓

AI Gateway

↓

Prompt Builder

↓

Context Builder

↓

Financial Engine

↓

LLM Provider

↓

Response Formatter

↓

Flutter
```

---

# Arquitectura

```text
AI Module

├── Chat
├── Insights
├── Predictions
├── Recommendations
├── OCR
├── Financial Score
├── Simulator
├── Monthly Reports
├── Weekly Reports
└── Analytics
```

---

# Estructura Backend

```text
ai/

controllers/

services/

repositories/

prompts/

providers/

models/

schemas/

utils/
```

---

# AI Gateway

Todos los servicios de IA deberán pasar por un único punto de entrada.

```text
AI Gateway

↓

Valida permisos

↓

Construye contexto

↓

Selecciona proveedor

↓

Genera respuesta

↓

Guarda historial
```

---

# AI Provider

El proveedor debe ser desacoplado.

Interfaz

```python
AIProvider

generate()

embeddings()

vision()

speech()
```

Implementaciones

- OpenAI
- Claude
- Gemini
- Ollama (Local)
- Azure OpenAI

El resto del sistema nunca conocerá el proveedor.

---

# Prompt Builder

Los prompts nunca estarán hardcodeados.

Se almacenarán como plantillas.

Ejemplo

```text
prompts/

weekly_summary.md

financial_score.md

goal_prediction.md

expense_analysis.md
```

---

# Context Builder

Antes de enviar una pregunta al modelo se construirá contexto.

Información incluida

Usuario

Pareja

Mes actual

Saldo

Ingresos

Gastos

Metas

Presupuesto

Historial

KPIs

---

# Contexto Máximo

Nunca enviar información innecesaria.

Solo:

Últimos 12 meses.

---

# Chat Financiero

Pantalla

AI Chat

Permite preguntas como

¿Cuánto gasté este mes?

¿Cuánto hemos ahorrado?

¿Quién ha aportado más?

¿Cuál fue nuestro gasto más grande?

---

# Ejemplo

Usuario

```
¿Cuánto gastamos en restaurantes?
```

↓

Respuesta

```
Durante este mes gastaron
$840.000 COP.

Representa el 18% del presupuesto mensual.

Es un 12% más que el mes pasado.
```

---

# Insights Automáticos

Cada semana

La IA generará:

- Resumen semanal
- Oportunidades de ahorro
- Gastos inusuales
- Riesgos
- Felicitaciones

---

Ejemplo

```
Esta semana redujeron un 14%
el gasto en transporte.

Excelente trabajo.
```

---

# Reporte Mensual

Cada inicio de mes.

La IA generará automáticamente.

Incluye

Ingresos

Gastos

Ahorro

KPIs

Comparación

Predicciones

---

# Recomendaciones

Ejemplos

```
Reduciendo un café diario
podrían ahorrar
$180.000 al mes.
```

---

```
Si mantienen este ritmo,
cumplirán la meta del viaje
32 días antes.
```

---

# Detección de Patrones

Detectar automáticamente

- Gastos repetitivos
- Compras impulsivas
- Categorías dominantes
- Horarios de gasto
- Días con mayor consumo

---

Ejemplo

```
Los viernes concentran
el 28% de sus gastos.
```

---

# Predicciones

La IA deberá estimar

Saldo fin de mes.

Ahorro.

Cumplimiento metas.

Liquidez.

Flujo de caja.

---

Ejemplo

```
Saldo estimado

$2.430.000
```

---

# Simulador Financiero

Permite preguntas

```
¿Qué pasa si ahorramos
300.000 adicionales?
```

---

```
¿Y si dejamos de pedir
domicilios?
```

---

```
¿Podemos comprar
una moto en diciembre?
```

---

# Financial Score

Calificación

0 — 100

Factores

Presupuesto

Ahorro

Liquidez

Constancia

Pagos

Deudas

---

Ejemplo

```
Score

91/100
```

---

Explicación

```
Excelente manejo financiero.

El único punto por mejorar
es reducir gastos en ocio.
```

---

# Salud Financiera

Indicadores

Liquidez

Capacidad de ahorro

Estabilidad

Dependencia

Balance

---

Resultado

Excelente

Bueno

Regular

Crítico

---

# OCR de Facturas

Tomar fotografía.

↓

Vision Model

↓

Extraer

Comercio

Fecha

IVA

Productos

Total

↓

Crear gasto automáticamente.

---

# OCR Campos

Nombre comercio

Fecha

Hora

Subtotal

IVA

Total

Moneda

Categoría sugerida

---

# Clasificación Inteligente

La IA sugerirá

Categoría

Subcategoría

Etiquetas

Prioridad

---

# Gastos Atípicos

Detectar automáticamente.

Ejemplo

```
Este gasto supera
en 180%
tu promedio.
```

---

# Alertas Inteligentes

Ejemplos

```
Este mes ya alcanzaste
el 90%
del presupuesto
en restaurantes.
```

---

```
Tu meta del carro
podría retrasarse
dos meses.
```

---

# Comparaciones

Comparar

Semana

Mes

Año

Categorías

Usuarios

Pareja

---

# Ranking

Mostrar

Mayor gasto

Mayor ahorro

Mayor aporte

Categoría dominante

---

# IA Conversacional

Debe recordar

Contexto conversación.

Historial reciente.

Objetivos.

Preferencias.

---

# Historial

Guardar

Pregunta

Respuesta

Tokens

Costo

Tiempo

Proveedor

---

# Caché

Preguntas repetidas

↓

Redis

↓

Evitar consumo innecesario.

---

# Costos

Registrar

Tokens entrada.

Tokens salida.

Costo USD.

Proveedor.

Modelo.

---

# Modelos

Chat

GPT

Claude

Gemini

---

Vision

GPT Vision

Claude Vision

Gemini Vision

---

Embeddings

OpenAI

BGE

Instructor XL

---

# Seguridad

Nunca enviar

Contraseñas.

JWT.

Tokens.

Información bancaria.

Datos sensibles.

---

# Privacidad

La IA solo podrá acceder a:

Información del usuario autenticado.

Nunca de otros usuarios.

---

# Feedback

El usuario podrá calificar

👍

👎

Cada respuesta.

---

# Aprendizaje

Guardar

Feedback

↓

Mejorar prompts.

Nunca entrenar modelos con información privada sin consentimiento.

---

# Dashboard IA

Widgets

Financial Score

Insights

Predicciones

Recomendaciones

Metas

Riesgos

---

# Arquitectura Futura (RAG)

```text
Usuario

↓

Pregunta

↓

Retriever

↓

Base Vectorial

↓

Contexto

↓

LLM

↓

Respuesta
```

Base Vectorial

- pgvector
- Pinecone
- Weaviate
- Qdrant

---

# Machine Learning (Futuro)

Modelos propios

Predicción gastos.

Clasificación.

Fraude.

Anomalías.

Forecast.

---

# KPIs IA

Tiempo respuesta

Costo

Tokens

Satisfacción

Accuracy

Preguntas resueltas

---

# Testing

Casos

Prompts.

Respuestas.

Hallucinations.

OCR.

Simulaciones.

Predicciones.

---

# Objetivo Final

Together no debe ser únicamente una aplicación para registrar gastos.

Debe convertirse en un **Asistente Financiero Inteligente para Parejas**, capaz de analizar, explicar, proyectar y acompañar a los usuarios en la construcción de una vida financiera saludable.

La IA debe convertir datos financieros en decisiones inteligentes, manteniendo siempre la privacidad, la transparencia y la confianza del usuario.