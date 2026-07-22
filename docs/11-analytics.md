# 📊 Together

# Documento 11 — Analytics & Business Intelligence

**Versión:** 1.0

**Estado:** Aprobado

**Módulo:** Analytics

---

# Objetivo

El módulo Analytics tiene como objetivo convertir todos los movimientos financieros registrados en Together en información útil para la toma de decisiones.

No se limita a mostrar gráficos.

Debe responder preguntas como:

- ¿En qué estamos gastando más?
- ¿Estamos mejor que el mes pasado?
- ¿Qué hábitos están afectando nuestras metas?
- ¿Quién aporta más?
- ¿Qué tan saludable es nuestra economía?
- ¿Cómo podemos ahorrar más?

---

# Filosofía

Los datos deben responder preguntas.

Nunca mostrar gráficos únicamente porque "se ven bonitos".

Cada visualización debe tener un propósito.

---

# Arquitectura

```text
PostgreSQL

↓

Financial Rules Engine

↓

Analytics Service

↓

KPIs

↓

Charts

↓

Dashboard

↓

Flutter
```

---

# Principios

Todos los indicadores deberán cumplir:

- Exactitud
- Rapidez
- Consistencia
- Explicabilidad
- Escalabilidad

---

# Dashboards

La aplicación tendrá cuatro dashboards.

---

# Dashboard 1

## Personal

Solo visible para el propietario.

Información:

- Saldo
- Ingresos
- Gastos
- Flujo de caja
- Presupuesto
- Categorías
- Tendencias

---

# Dashboard 2

## Compartido

Visible para ambos integrantes.

Información:

- Balance conjunto
- Aportes
- Gastos
- Deudas
- Metas
- Score financiero

---

# Dashboard 3

## IA

Información generada por IA.

Incluye

- Insights
- Recomendaciones
- Riesgos
- Predicciones

---

# Dashboard 4

## Metas

Visualiza

- Progreso
- Tiempo restante
- Aportes
- Predicciones

---

# KPIs Personales

## KPI-001

Saldo actual

```
Ingresos - Gastos
```

---

## KPI-002

Ingresos del mes

---

## KPI-003

Gastos del mes

---

## KPI-004

Ahorro mensual

---

## KPI-005

Ahorro anual

---

## KPI-006

Promedio diario de gasto

---

## KPI-007

Promedio semanal

---

## KPI-008

Promedio mensual

---

## KPI-009

Mayor gasto

---

## KPI-010

Categoría dominante

---

## KPI-011

Número de movimientos

---

## KPI-012

Presupuesto consumido

---

## KPI-013

Liquidez

---

## KPI-014

Cash Flow

---

## KPI-015

Variación respecto al mes anterior

---

# KPIs Compartidos

## KPI-016

Saldo conjunto

---

## KPI-017

Total aportado

---

## KPI-018

Total gastado

---

## KPI-019

Deuda pendiente

---

## KPI-020

Aporte de cada integrante

---

## KPI-021

Porcentaje de participación

---

## KPI-022

Meta principal

---

## KPI-023

Progreso total

---

## KPI-024

Financial Score

---

## KPI-025

Health Score

---

# KPIs IA

## KPI-026

Riesgo financiero

---

## KPI-027

Probabilidad de cumplir metas

---

## KPI-028

Gastos anómalos

---

## KPI-029

Nivel de disciplina

---

## KPI-030

Nivel de ahorro

---

# Visualizaciones Permitidas

## Cards

Para KPIs.

---

## Line Chart

Tendencias.

Ingresos

Gastos

Ahorros

---

## Area Chart

Evolución.

---

## Bar Chart

Comparaciones.

---

## Horizontal Bar

Rankings.

---

## Donut

Distribución.

Máximo 6 categorías.

---

## Radar

Perfil financiero.

---

## Heatmap

Días con mayor gasto.

---

## Calendar Heatmap

Actividad diaria.

---

## Progress Bar

Metas.

---

## Sparkline

Mini tendencias.

---

# Visualizaciones NO Permitidas

No utilizar

- Pie Charts tradicionales
- Gauge
- 3D Charts
- Treemap
- Funnel
- Radar con demasiadas variables

---

# Dashboard Principal

Orden

```
Saludo

↓

Balance

↓

KPIs

↓

Gráfica principal

↓

Actividad reciente

↓

Metas

↓

Insights IA

↓

Recordatorios
```

---

# Métricas Personales

Calcular

- Gasto promedio diario
- Gasto promedio mensual
- Categoría favorita
- Día con mayor consumo
- Hora con mayor consumo
- Tendencia

---

# Métricas Compartidas

Calcular

- Quién aporta más
- Quién registra más gastos
- Distribución de gastos
- Evolución del ahorro
- Balance mensual

---

# Tendencias

Mostrar

Últimos

7 días

30 días

90 días

1 año

Todo

---

# Comparaciones

Permitir comparar

Mes vs Mes

Año vs Año

Categoría vs Categoría

Usuario vs Usuario

Meta vs Meta

---

# Rankings

Top categorías

Top gastos

Top ingresos

Top comercios

Top metas

---

# Segmentación

Filtros

Fecha

Usuario

Categoría

Monto

Método de pago

Etiquetas

---

# Predicciones

Mostrar

Saldo esperado

Ahorro esperado

Cumplimiento metas

Flujo de caja

---

# Dashboard de Metas

Mostrar

Monto objetivo

Monto actual

Tiempo restante

Predicción

Aportes

Gráfica

---

# Dashboard IA

Mostrar

Financial Score

Health Score

Insights

Consejos

Predicciones

Alertas

---

# Exportaciones

Permitir exportar

PDF

Excel

CSV

---

# Reportes

Automáticos

Semanales

Mensuales

Anuales

---

# Alertas Analíticas

Ejemplos

```
Los gastos aumentaron
18%
respecto al mes anterior.
```

---

```
Este mes alcanzaste
el 90%
del presupuesto.
```

---

```
Su ahorro creció
12%.
```

---

# Dashboard Responsive

Mobile

Tablet

Desktop

---

# Colores

Verde

Indicadores positivos

Rojo

Indicadores negativos

Amarillo

Advertencias

Azul

Información

Rosa

Marca Together

---

# Rendimiento

Todas las consultas deberán responder en

< 500 ms

Siempre que sea posible.

---

# Materialized Views

Crear vistas para

Dashboard

KPIs

Resumen mensual

Resumen anual

Ranking categorías

Ranking gastos

---

# Cache

Redis

Cache

Dashboard

KPIs

Reportes

Insights

---

# Actualización

Dashboard

Tiempo real

o

Cada 60 segundos

---

# Cálculos

Todos los KPIs deberán calcularse mediante el Financial Rules Engine.

Nunca mediante IA.

La IA únicamente explicará los resultados.

---

# Data Warehouse (Futuro)

```text
OLTP

↓

ETL

↓

Data Warehouse

↓

Power BI

↓

Analytics
```

---

# Eventos

Registrar eventos

Login

Registro

Nuevo gasto

Nueva meta

Nuevo aporte

Pago deuda

Consulta IA

---

# Métricas del Producto

Usuarios activos

DAU

WAU

MAU

Retención

Churn

Sesiones

Tiempo promedio

Pantallas más utilizadas

Errores

---

# Observabilidad

Integrar

Firebase Analytics

Crashlytics

CloudWatch

---

# Machine Learning (Futuro)

Modelos

Forecast

Segmentación

Clasificación

Anomalías

Fraude

---

# Testing

Validar

Todos los KPIs

Todas las consultas

Todos los filtros

Todas las exportaciones

Todas las visualizaciones

---

# Principio Final

Analytics es el cerebro analítico de Together.

No debe limitarse a mostrar datos.

Debe ayudar a que las personas comprendan su comportamiento financiero, identifiquen oportunidades de mejora y tomen decisiones más inteligentes.

Cada indicador, gráfico o reporte deberá aportar valor real al usuario y estar respaldado por cálculos consistentes provenientes del Financial Rules Engine.