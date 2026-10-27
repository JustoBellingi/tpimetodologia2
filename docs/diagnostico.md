# Diagnóstico de la versión inicial (tag `estado-inicial`)

Archivo analizado: `app.py` (347 líneas, 1 clase `Sistema` con 8 métodos + `main`).

## Calidad externa vs. interna
- **Externa (lo que ve el usuario): correcta.** Las 5 operaciones funcionan, valida datos,
  respeta las reglas de estado y persiste en `datos.json`.
- **Interna (lo que ve quien mantiene el código): débil.** Todo vive en una clase,
  hay lógica copiada y pegada, códigos mágicos y errores silenciados.
  Agregar un estado, un tipo o un filtro obliga a tocar 4–6 lugares.

## Code smells detectados

| # | Smell | Ubicación (app.py) | Evidencia | Impacto | Riesgo de mantenimiento | Prioridad |
|---|---|---|---|---|---|---|
| S1 | God Class | `Sistema`, l. 12–295 | Persistencia, validación, reglas, búsquedas, reporte y catálogo en una clase | Cualquier cambio toca la misma clase | Alto: conflictos y regresiones | Alta |
| S2 | Long Method | `registrar` l. 37–88, `buscar` l. 170–229, `reporte` l. 231–282 | Métodos de 50–60 líneas con varias responsabilidades | Difícil de leer y testear | Alto | Alta |
| S3 | Long Parameter List | `registrar(nom, leg, mail, tipo, desc, prio)` l. 37 | 6 strings seguidos | Fácil invertir argumentos sin error | Medio | Media |
| S4 | Duplicated Code | `json.dump` l. 84, 130, 164; búsqueda por id l. 91–97 y 143–149; formato de línea l. 229 y 279; búsqueda de responsable l. 154, 226 y 276 | Mismo bloque copiado | Un cambio debe repetirse N veces | Alto: olvidar una copia | Alta |
| S5 | Primitive Obsession / Magic Strings | `"P"`, `"E"`, `"R"`, `"X"`, `"CERTIFICADO"`, solicitudes como `dict` | Estados y tipos como strings sueltos | Un typo no da error, falla en silencio | Alto | Alta |
| S6 | Switch Statements | cadenas `if/elif` de tipo (l. 59, 190), estado (l. 99, 174, 217), transiciones (l. 109–124) | Misma decisión repetida | Agregar un valor obliga a editar todas las cadenas (viola OCP) | Medio | Media |
| S7 | Nombres poco expresivos | `lst`, `cont`, `x`, `s`, `d`, `n`, `e`, `t`, `rn`, `c1..c4`, `id` (pisa builtin) | Hay que leer el contexto para entender | Lento de leer | Medio | Media |
| S8 | Manejo de errores deficiente | `except:` l. 32 y l. 342; `return -1/False/None` | Archivo corrupto se reinicia y se sobrescribe; error genérico; el `except:` del menú no cubre el `input` de la opción: con fin de entrada (EOF) el programa termina con un traceback | Pérdida de datos y fallas ocultas | Alto | Alta |
| S9 | Dependencias ocultas | `ARCHIVO` global l. 9, `open()` directo, `datetime.now()` l. 79 | La lógica depende del disco y del reloj | No se puede testear sin archivos reales (viola DIP) | Alto | Alta |
| S10 | Presentación mezclada con negocio | `print` dentro de `registrar`, `cambiar_estado`, `asignar`, `buscar`, `reporte` | La lógica no se puede reusar (web, API) | Bajo reúso | Medio | Media |
| S11 | Data Clumps | `nom`, `leg`, `mail` viajan juntos | No existe la entidad Estudiante | Datos del estudiante dispersos | Bajo | Media |
| S12 | Dead Code y comentarios redundantes | `calcular_prioridad` l. 290 sin uso; `exportar_csv` comentado l. 284–288; `# guardar` | Código que nadie llama | Confunde al lector | Bajo | Baja |
