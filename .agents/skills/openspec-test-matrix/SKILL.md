---
name: openspec-test-matrix
description: Genera una matriz de casos de prueba formateada en tabla (con estado 'Pendiente') a partir de todas las especificaciones (specs) de un cambio en OpenSpec.
---

# Generador de Matriz de Casos de Prueba desde OpenSpec Specs

Esta skill analiza automáticamente los archivos `specs/**/*.md` de un cambio en OpenSpec y construye una matriz de casos de prueba estructurada en una tabla Markdown con el estado fijado en **`Pendiente`**, lista para copiar y pegar en Excel o Google Sheets.

## Entrada

- Nombre del cambio en OpenSpec (ej. `add-auth-module` o `/opsx-test-matrix add-auth-module`).
- Si no se especifica, deduce el cambio activo ejecutando `openspec list --json` o `openspec status --json`.

## Flujo de Ejecución

1. **Identificar el cambio objetivo**
   - Obtener el nombre del cambio.
   - Ejecutar `openspec status --change "<nombre-del-cambio>" --json` para verificar la existencia de artefactos de especificación (`specs`).

2. **Leer todos los archivos de especificación (`specs`)**
   - Leer todos los archivos contenidos en `openspec/changes/<nombre-del-cambio>/specs/**/*.md`.

3. **Extraer Requerimientos y Escenarios**
   Para cada archivo `spec.md` encontrado:
   - Identificar el nombre de la capacidad (nombre de la subcarpeta dentro de `specs/`).
   - Extraer cada `### Requirement: <Nombre del Requerimiento>`.
   - Extraer cada `#### Scenario: <Nombre del Escenario>`.
   - Extraer la condición de entrada desde la línea `- **WHEN** ...`.
   - Extraer el resultado esperado desde la línea `- **THEN** ...`.

4. **Clasificar el Tipo de Prueba**
   Categorizar automáticamente el escenario en uno de los siguientes tipos:
   - **Positiva**: Casos felices, creación exitosa, respuestas `200 OK`, `201 Created`.
   - **Negativa**: Entradas inválidas, recursos no encontrados, duplicados (`400`, `404`, `409`).
   - **Limite**: Longitudes de campos, fechas pasadas/expiradas, límites de tamaño (ej. clave < 8 caracteres, token expirado).
   - **Borde de Seguridad**: Tasa de peticiones (`429 Rate limit`), anti-enumeración, control de acceso RBAC (`401`, `403`).

5. **Generar el ID del Caso de Prueba**
   - Formato: `TC-<CAPACIDAD_CORROBORADA>-001`, `TC-<CAPACIDAD_CORROBORADA>-002`, etc.

6. **Construir y Presentar la Tabla**
   Formatear el resultado en una tabla Markdown estricta con las siguientes columnas:
   `ID | Capacidad (Spec) | Requerimiento (Req) | Escenario OpenSpec | Tipo de Prueba | Condiciones / Entradas (WHEN) | Resultado Esperado (THEN) | Estado`

   - Fijar la columna **Estado** con el valor **`Pendiente`** para todos los casos.
   - Entregar la respuesta en un bloque Markdown limpio para facilitar la copia directa a Google Sheets.
