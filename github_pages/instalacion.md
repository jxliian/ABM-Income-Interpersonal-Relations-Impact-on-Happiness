---
layout: default
title: Instalación
nav_order: 2
---

# Guía de Instalación

Esta página detalla cómo instalar y ejecutar el simulador tanto para usuarios que desean una prueba rápida en Windows como para desarrolladores o usuarios de Linux.

---

## Instalación Rápida (Windows)

Si usas **Windows** y quieres probar la aplicación rápidamente sin instalar nada (ni Python ni librerías), sigue estos pasos:

1.  **Descarga el repositorio base:** Pulsa en el botón verde `<> Code` y elige `Download ZIP`. Descomprime el archivo.
2.  **Descarga el ejecutable:** Ve a la pestaña **[Actions](https://github.com/jxliian/ABM-Income-Interpersonal-Relations-Impact-on-Happiness/actions)** del repositorio, entra en el último workflow ("Build Windows Executable") y descarga el artefacto `ABM_Happiness_Tool_Windows`.
3.  **Coloca el ejecutable:** Descomprime el artefacto y mueve el archivo `ABM_Happiness_Tool.exe` **DENTRO** de la carpeta del repositorio que descomprimiste en el paso 1 (debe estar junto a carpetas como `src`, `assets`, etc.).
4.  **Ejecuta:** Haz doble clic en `ABM_Happiness_Tool.exe`.

![Vista de la App](../assets/images/app.png)

> **Nota:** Al ejecutarlo, puede tardar unos segundos en cargar. Si Windows Defender muestra un aviso, pulsa en "Más información" -> "Ejecutar de todas formas".

> [!IMPORTANT]
> **Ventajas y Limitaciones**
> *    **Ventaja:** No hay que instalar nada.
> *    **Limitación:** Esta versión ejecuta únicamente el modelo de **Facebook**. No es posible seleccionar otras redes sociales ni usar el modo experimental. Para esas funciones, se recomienda usar la instalación manual con Conda (ver abajo).

---

## Instalación y Configuración (Linux / Desarrolladores)

Para garantizar que todos los miembros del equipo utilicen la misma pila tecnológica y evitar conflictos de librerías, este proyecto utiliza un entorno virtual definido en el archivo `environment.yml`.

### 1. Instalar Anaconda

Antes de comenzar, debes tener instalada la distribución de **Anaconda** o **Miniconda**, que incluye las herramientas necesarias para la gestión de entornos.

*   **Descarga:** [Web oficial de Anaconda](https://www.anaconda.com/download/success)
*   **Instalación:** Ejecuta el instalador descargado. Se recomienda usar la configuración predeterminada.

### 2. Crear el Entorno Conda

Una vez instalado Anaconda, abre **Anaconda Prompt** (Windows) o tu terminal (macOS/Linux) y navega hasta la carpeta raíz del proyecto.

Ejecuta el siguiente comando para crear automáticamente el entorno con todas las dependencias necesarias (`mesa`, `pandas`, `numpy`, etc.):

```bash
conda env create -f environment.yml
```

Este comando leerá el archivo y creará un entorno aislado llamado **`abm_seminario`**.

---

## Ejecutables

### Windows

Si prefieres usar el ejecutable generado automáticamente (alternativa al paso anterior):
1.  Ve a la pestaña **[Actions](https://github.com/jxliian/ABM-Income-Interpersonal-Relations-Impact-on-Happiness/actions)** del repositorio.
2.  Descarga el artefacto `ABM_Happiness_Tool_Windows` del último build.
3.  Descomprímelo y ejecuta el `.exe`.

### Linux (Experimental)

Existe un ejecutable en `./dist/ABM_Happiness_Tool` generado con PyInstaller.

> **Importante:** Actualmente, el ejecutable de Linux **solo implementa correctamente hasta el Paso 2**.
> Para una experiencia completa y estable en Linux, se recomienda encarecidamente **ejecutar el código fuente** siguiendo los pasos de "Uso del Entorno" (comando `python src/graphics.py`).
