# Pruebas y verificación del comportamiento (etapa 6)

## Estrategia
1. **Tests de caracterización (golden master).** Antes de refactorizar se grabó lo que hacía
   la versión inicial en 5 escenarios: la salida completa en pantalla y el `datos.json` final.
   Cada escenario se ejecuta como lo haría un usuario (mismas teclas, por entrada estándar).
2. **Tests unitarios.** Se escribieron sobre la versión nueva para las reglas que antes no se
   podían probar en aislamiento (dominio, validación, servicio, consola).
3. **Comparación directa antes/después.** `comparar_versiones.py` extrae `app.py` del tag
   `estado-inicial` y corre los mismos escenarios sobre las dos versiones.

## Casos de prueba de caracterización

| Escenario | Qué cubre | Líneas de salida | Errores esperados |
|---|---|---|---|
| `01_flujo_completo` | Registrar 3 solicitudes, asignar, pasar a EN PROCESO, RESUELTA y RECHAZADA, reporte y búsquedas por estado, tipo y legajo | 156 | 0 |
| `02_validaciones_registro` | Los 6 errores de validación del alta y un alta con espacios a recortar | 102 | 6 |
| `03_reglas_estado` | Transiciones inválidas, IDs y responsables inexistentes, solicitud cerrada, opción de menú inválida | 186 | 9 |
| `04_busquedas` | Criterio, estado y tipo inválidos, legajo sin resultados, legajo con varias solicitudes | 146 | 3 |
| `05_persistencia` | Arrancar con un `datos.json` existente, continuar el contador de IDs y guardar | 97 | 1 |

Cada escenario genera 2 tests (pantalla y datos): 10 tests en total.

## Tests unitarios (27)

| Archivo | Cantidad | Qué verifica |
|---|---|---|
| `test_dominio.py` | 7 | Estado inicial, reglas de transición, solicitudes cerradas, códigos de estado |
| `test_formulario.py` | 7 | Alta válida y cada uno de los 6 errores de validación |
| `test_servicio.py` | 11 | Casos de uso con repositorio en memoria **y** JSON (LSP), reporte, persistencia |
| `test_consola.py` | 2 | Mejoras intencionales: ID no numérico y fin de entrada |

## Evidencia de ejecución

```text
$ python -m pytest
37 passed

$ python -m tests.caracterizacion.comparar_versiones
Escenario                   Salida en pantalla    datos.json
----------------------------------------------------------------
01_flujo_completo           IGUAL                 IGUAL
02_validaciones_registro    IGUAL                 IGUAL
03_reglas_estado            IGUAL                 IGUAL
04_busquedas                IGUAL                 IGUAL
05_persistencia             IGUAL                 IGUAL
----------------------------------------------------------------
Sin diferencias.
```

## Cómo se verificó que el refactoring no alteró el comportamiento
- **La red se armó antes de tocar el código** (commit `2452a28`), grabada sobre `estado-inicial`.
- **La red detecta cambios:** se cambió a propósito el mensaje "ya esta" por "ya se encuentra"
  y fallaron 2 tests; luego se revirtió.
- **Cada commit del refactoring pasa la suite** en un checkout limpio:
  10 → 17 → 24 → 24 → 35 → 37 tests.
- **Los datos son compatibles:** el escenario 05 abre un `datos.json` creado con el formato
  de la versión inicial.
- **Cambios intencionales documentados:** ID no numérico y fin de entrada ahora dan mensajes
  claros (ver `decisiones-tecnicas.md`); están cubiertos por `test_consola.py`.

## Cómo repetirlo
```bash
pip install pytest
python -m pytest -v
python -m tests.caracterizacion.comparar_versiones
```
En Windows, si `python` no se reconoce, usar `py` en su lugar.
