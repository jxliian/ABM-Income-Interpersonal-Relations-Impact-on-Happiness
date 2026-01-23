---
layout: default
title: Metodología y Modelo
nav_order: 2
---

# Hipótesis, Datos y Metodología
{: .fs-9 }

Este epígrafe se estructura en tres bloques fundamentales para la validación empírica de la investigación. En primer lugar, se formaliza el modelo analítico. En segundo lugar, se describen los microdatos. Finalmente, se detalla la metodología computacional.

## Modelo Analítico e Hipótesis

El modelo teórico se fundamenta en la premisa de que el bienestar subjetivo ($H$) no es una variable exógena, sino el resultado de una función de producción de utilidad que combina **Capital Económico ($E$)** y **Tiempo Disponible ($R$)**. Formalizamos esta relación mediante una función **Cobb-Douglas** adaptada, donde el parámetro $\alpha$ representa la elasticidad cultural o "materialismo" del agente:

$$ H_{i,t=0} = (E_{i}^{\alpha} \cdot R_{i}^{1-\alpha}) $$
{: .text-center .p-4 .bg-grey-dk-000 .rounded }

### Resonancia Social Inversa
Adicionalmente, introducimos la hipótesis de la Resonancia Social Inversa, que postula que la capacidad de interacción social ($S$) depende de la felicidad acumulada:

$$ S_i = H_i \cdot (1 + H_i^{1-\alpha}) $$

## Datos y Fuentes (CIS)

Para la calibración empírica del modelo, se han utilizado los microdatos del **Estudio 3145 del Centro de Investigaciones Sociológicas (CIS)**. La base de datos original ha sido depurada para extraer una submuestra representativa de usuarios activos en redes sociales (Facebook, Instagram y X/Twitter).

Las variables seleccionadas son:
*   **Ingresos ($E$)**: Variable `P65` (Ingresos netos mensuales), normalizada en escala 1-10.
*   **Tiempo ($R$)**: Calculada a partir de `P60A` (Jornada laboral), definiendo el tiempo disponible como el remanente de una jornada estándar.
*   **Felicidad Declarada ($H_{real}$)**: Variable `P69`, utilizada para validación inicial.

## Metodología ABM (Agent-Based Modeling)

Para el análisis empírico, se ha implementado un modelo en **Python** utilizando la librería **Mesa**. El entorno de simulación es una grilla toroidal de $30 \times 30$, poblada por $N = 300$ agentes.

### Reglas de Operación
1.  **Evaluación de Entorno**: Cada agente escanea su vecindad de Moore.
2.  **Regla de Movimiento (Segregación)**: Si la disonancia económica supera un umbral $\delta$ o la felicidad cae por debajo de un nivel crítico ($H < 2.5$), el agente busca una nueva ubicación (Dinámica de Schelling).
3.  **Actualización de Estado**: En cada paso, los agentes recalculan su felicidad integrando el impacto del salario y la influencia emocional de sus vecinos.

> **Nota Técnica:** Esta metodología permite aislar el efecto de variables específicas (como $\alpha$) y observar la evolución temporal de la segregación.
