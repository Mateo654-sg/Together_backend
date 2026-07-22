# 🧮 Together

# Documento 17 — Financial Rules Engine

**Versión:** 1.0

**Estado:** Oficial

**Tipo:** Core Business Engine

---

# Objetivo

El Financial Rules Engine (FRE) es el núcleo matemático de Together.

Toda decisión financiera deberá calcularse aquí.

La Inteligencia Artificial nunca realizará cálculos financieros.

Su única responsabilidad será interpretar los resultados producidos por este motor.

---

# Filosofía

Los cálculos financieros deben ser:

- Exactos
- Reproducibles
- Auditables
- Determinísticos
- Testeables

Dos usuarios con exactamente la misma información siempre deberán obtener exactamente el mismo resultado.

---

# Responsabilidades

El Financial Rules Engine será responsable de:

- Balance personal
- Balance compartido
- Deudas
- Liquidaciones
- KPIs
- Presupuestos
- Metas
- Predicciones matemáticas
- Financial Score
- Health Score
- Riesgo financiero
- Liquidez
- Cash Flow
- Forecast

---

# Arquitectura

```text
Movimientos

↓

Financial Rules Engine

↓

Resultados

↓

Analytics

↓

IA

↓

Flutter
```

---

# Principios

La IA nunca modifica resultados.

El Frontend nunca calcula indicadores.

La Base de Datos nunca contiene lógica.

Toda regla vive aquí.

---

# Organización

```text
financial_engine/

balances/

budgets/

cashflow/

debts/

forecast/

goals/

health/

income/

insights/

kpis/

liquidity/

predictions/

scores/

statistics/

utils/
```

---

# Motor 1

## Balance Personal

### Definición

Dinero disponible para un usuario.

---

### Fórmula

```
Balance =
Ingresos
-
Gastos
```

---

### Ejemplo

Ingresos

4.000.000

Gastos

2.300.000

Resultado

1.700.000

---

# Motor 2

## Balance Compartido

```
Aportes Totales

-

Gastos Compartidos
```

---

Ejemplo

Mateo

600.000

Laura

700.000

Total

1.300.000

Mercado

300.000

Viaje

200.000

Saldo

800.000

---

# Motor 3

## Deudas

Regla

Cada gasto genera automáticamente una distribución.

Ejemplo

Mercado

200.000

Pagó

Mateo

División

50/50

Resultado

Laura debe

100.000

---

Si

70/30

Resultado

Mateo

140.000

Laura

60.000

---

# Motor 4

## Cash Flow

```
Ingresos

-

Gastos

=

Flujo Neto
```

---

Clasificación

Positivo

Negativo

Neutro

---

# Motor 5

## Liquidez

```
Saldo Disponible

/

Gastos Promedio Mensuales
```

---

Resultado

Excelente

Buena

Aceptable

Crítica

---

# Motor 6

## Burn Rate

```
Gastos

/

Días
```

---

Indica

Velocidad de consumo del dinero.

---

# Motor 7

## Saving Rate

```
Ahorro

/

Ingresos

×

100
```

---

Clasificación

Excelente

>30%

Buena

20-30%

Regular

10-20%

Crítica

<10%

---

# Motor 8

## Budget Consumption

```
Gastado

/

Presupuesto

×

100
```

---

Alertas

80%

90%

100%

120%

---

# Motor 9

## Goal Progress

```
Monto Actual

/

Meta

×

100
```

---

Ejemplo

Meta

10.000.000

Ahorro

4.500.000

Resultado

45%

---

# Motor 10

## Goal Forecast

Estimar

Fecha de cumplimiento

Basado en

Promedio ahorro últimos meses.

---

Ejemplo

Meta

10.000.000

Ahorro mensual

500.000

Resultado

11 meses

---

# Motor 11

## Debt Score

Evalúa

Número de deudas.

Monto.

Tiempo pendiente.

---

Escala

0-100

---

# Motor 12

## Financial Score

Escala

0-100

---

Factores

Saving Rate

25%

Budget Control

20%

Debt

20%

Liquidity

15%

Goals

10%

Cash Flow

10%

---

Resultado

Excelente

90+

Bueno

75-89

Regular

60-74

Crítico

<60

---

# Motor 13

## Financial Health

Evalúa

Liquidez

Ahorro

Presupuesto

Deudas

Metas

---

Resultado

Excelente

Bueno

Regular

Crítico

---

# Motor 14

## Couple Balance Index

Nuevo indicador exclusivo.

Mide

Equilibrio financiero entre ambos.

Variables

Participación.

Deudas.

Aportes.

Cumplimiento.

---

Resultado

0-100

---

# Motor 15

## Spending Trend

Analiza

7 días

30 días

90 días

365 días

---

Resultado

Creciente

Estable

Decreciente

---

# Motor 16

## Category Dominance

Calcula

```
Categoría

/

Gasto Total
```

---

Ejemplo

Comida

38%

---

# Motor 17

## Weekly Average

```
Total

/

Semanas
```

---

# Motor 18

## Monthly Average

```
Total

/

Meses
```

---

# Motor 19

## Year Projection

Predice

Saldo

Gastos

Ahorro

al finalizar el año.

---

# Motor 20

## Forecast Engine

Calcula

Saldo futuro.

Metas.

Liquidez.

Presupuesto.

---

Nunca utiliza IA.

Solo matemáticas.

---

# Alert Engine

Genera automáticamente

Presupuesto agotado.

Meta retrasada.

Deuda pendiente.

Exceso gasto.

Riesgo liquidez.

---

# Rule Priority

Critical

High

Medium

Low

---

# Eventos

Cada cálculo genera

Timestamp

Usuario

Motor

Resultado

Duración

---

# Cache

Todos los resultados

↓

Redis

↓

Reducir consultas.

---

# Testing

Cada motor tendrá

100%

Unit Tests.

---

Ejemplo

Balance

10 casos.

Deudas

20 casos.

Forecast

30 casos.

Financial Score

50 casos.

---

# Versionado

Cada cambio de regla incrementará la versión.

Ejemplo

Financial Score

v1

↓

v2

↓

v3

Nunca modificar resultados históricos.

---

# IA

La IA únicamente recibe

```json
{
 "financial_score":91,
 "saving_rate":28,
 "budget":84,
 "forecast":"11 meses"
}
```

Nunca realiza cálculos.

Solo responde

```
Su salud financiera es excelente.

Manteniendo este ritmo podrán cumplir su meta del viaje un mes antes de lo previsto.
```

---

# Auditoría

Todo cálculo importante será registrable para fines de trazabilidad.

Cada resultado debe poder reconstruirse a partir de los datos originales y de la versión del motor utilizada.

---

# Rendimiento

Objetivos

Balance

<20 ms

KPIs

<100 ms

Dashboard completo

<250 ms

Forecast

<500 ms

---

# Principio Final

El Financial Rules Engine es el corazón de Together.

Toda decisión financiera deberá originarse aquí.

La IA interpreta.

Analytics visualiza.

Flutter presenta.

Pero únicamente el Financial Rules Engine tiene autoridad para calcular la realidad financiera del usuario.