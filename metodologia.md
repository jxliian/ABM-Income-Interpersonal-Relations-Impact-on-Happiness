---
layout: default
title: Metodología y Modelo
nav_order: 2
---

# Metodología y Datos
[cite_start]Se implementa un Modelo Basado en Agentes (ABM) en Python para simular la interacción de individuos autónomos[cite: 30, 54].

## El Modelo Analítico
[cite_start]El bienestar subjetivo ($H$) se modela mediante una función **Cobb-Douglas** adaptada, donde $\alpha$ es el "materialismo" y $R$ es el tiempo disponible[cite: 50, 87]:

[cite_start]$$H_{i,t=0} = (E_{i}^{\alpha} \cdot R_{i}^{1-\alpha})$$ [cite: 88]

## Datos Reales (CIS)
[cite_start]Para calibrar a los agentes se usaron datos del Estudio 3145 del CIS[cite: 100], seleccionando variables clave:
* **Ingresos (P65):** Normalizados en escala 1-10[cite: 103].
* [cite_start]**Tiempo (P60A):** Calculado a partir de la jornada laboral[cite: 104].
