# Code review (etapa 7)

Revisión aplicada sobre `main` después del tag `etapa-pruebas` (commit `1a6ce8e`).
Combina revisión manual, uso real del sistema y chequeos automáticos
(`pytest`, `pyflakes`, búsquedas con `grep` y un script de `ast` para medir funciones).

## Checklist técnico

Resultado **antes** de las correcciones. ✔ cumple · ✘ no cumple · ⚠ cumple con observaciones.

| # | Área | Criterio | Cómo se verifica | Resultado | Observación |
|---|---|---|---|---|---|
| 1 | Funcionalidad | Todos los tests pasan | `python -m pytest` | ✔ | 37 passed |
| 2 | Funcionalidad | Los cambios de comportamiento están documentados y testeados | `decisiones-tecnicas.md`, `test_consola.py` | ✔ | |
| 3 | Diseño | Cada módulo tiene una sola responsabilidad (SRP) | Lectura de `solicitudes/` | ✔ | |
| 4 | Diseño | El dominio no depende de consola ni de persistencia | Imports de `dominio.py` | ✔ | Solo biblioteca estándar |
| 5 | Diseño | Solo la consola usa `print` / `input` | `grep "print(\|input("` | ✔ | |
| 6 | Diseño | Agregar un criterio de búsqueda no modifica el servicio (OCP) | Ver C2 | ✔ | Confirmado al aplicar C2 |
| 7 | Clean Code | Nombres expresivos, sin abreviaturas | Lectura | ✔ | |
| 8 | Clean Code | Funciones de 20 líneas o menos | Script `ast` | ✔ | Máxima: 18 (`Consola.__init__`) |
| 9 | Clean Code | Funciones con 4 parámetros o menos | Script `ast` | ✔ | |
| 10 | Clean Code | Sin código muerto ni imports sin uso | `pyflakes` | ✘ | O1 |
| 11 | Errores | Sin `except:` genérico | `grep "except:"` | ✔ | |
| 12 | Errores | Los errores se informan apenas se detectan | Uso del sistema | ✘ | O2 |
| 13 | Errores | Un archivo de datos dañado no provoca pérdida de datos | Prueba manual con JSON roto | ✘ | O3 |
| 14 | Usabilidad | El usuario puede consultar los IDs existentes | Uso del sistema | ✘ | O4 |
| 15 | Pruebas | Toda corrección tiene un test que la cubre | Revisión de cada commit | ✔ | Se exigió en C1 a C3 |
| 16 | Pruebas | Un cambio en el golden master se aprueba revisando la diferencia | `aprobar_cambio.py` + `docs/evidencias/` | ✔ | Se creó para esta etapa |
| 17 | Repositorio | README con instalación, uso, funcionalidades y tecnologías | Lectura | ⚠ | O5 |
| 18 | Repositorio | Tags obligatorios presentes | `git tag` | ⚠ | Faltan `etapa-docs` y `estado-refactorizado` (se crean al cerrar) |
| 19 | Repositorio | Commits con mensajes descriptivos | `git log` | ✔ | |
| 20 | Repositorio | Autoría identificable por integrante | `git log --format=%an` | ✘ | O6 |
| 21 | Datos | Solo datos sintéticos | Escenarios y ejemplos | ✔ | Nombres y legajos inventados |

## Observaciones y feedback

| ID | Severidad | Observación | Feedback | Acción |
|---|---|---|---|---|
| O1 | Baja | `consola.py` importa `generar_reporte` y no lo usa | Quedó del armado inicial. Un import sin uso confunde sobre las dependencias reales del módulo | Corregido en **C1** |
| O2 | Media | Con un ID inexistente, "Cambiar estado" y "Asignar responsable" piden más datos y recién al final avisan el error | Detectado al usar el sistema. El usuario carga datos que se descartan. Conviene validar en cuanto se tiene el dato | Corregido en **C1** |
| O3 | Alta | Si `datos.json` está dañado se arranca vacío y el próximo guardado lo sobrescribe | Era el riesgo de pérdida de datos señalado en la etapa 2 y quedó pendiente para no cambiar comportamiento en el refactoring. Corresponde corregirlo en la revisión | Corregido en **C3** |
| O4 | Media | No hay forma de listar todas las solicitudes; para operar hay que recordar los IDs | Detectado al usar el sistema. Es una necesidad básica del operador | Corregido en **C2** |
| O5 | Baja | El README no menciona `py` en Windows, ni la opción nueva, ni cómo repetir la comparación antes/después | La documentación debe acompañar al código | Corregido en **C4** |
| O6 | Media | Todos los commits figuran con el autor genérico "Equipo TPI" | La consigna pide participación demostrable. Desde ahora cada integrante debe commitear con su propio usuario | Pendiente (acción del equipo) |
| O7 | Baja | El catálogo de responsables está fijo en el código | Agregar un responsable requiere cambiar código. Aceptable para el alcance del TP | Pendiente, aceptado |
| O8 | Baja | `ejecutor.py` distingue las fechas precargadas porque empiezan con `2026-09` | Funciona, pero depende de una fecha mágica. Sería más robusto marcar esas solicitudes de otra forma | Pendiente, aceptado |

## Correcciones realizadas

| Código | Commit | Cambio | Test que lo cubre |
|---|---|---|---|
| C1 | `0fd4e09` | Validar el ID antes de pedir estado o responsable; quitar import sin uso | `test_asignar_a_un_id_inexistente_...`, `test_cambiar_estado_de_un_id_inexistente_...`, escenario 03 |
| C2 | `8820ce3` | Criterio de búsqueda `4-Todas` como clase nueva, sin tocar el servicio | `test_la_opcion_todas_...`, `test_un_criterio_invalido_...`, escenario 04 |
| C3 | `69d5952` | Apartar `datos.json` dañado, avisar y escribir de forma atómica | `test_un_archivo_danado_...`, `test_un_archivo_sano_...` |
| C4 | `9afa8e5` | README y documentación actualizados | — |

Las diferencias aprobadas en los escenarios están en `docs/evidencias/`
(`C1_03_reglas_estado.diff`, `C2_01_...`, `C2_03_...`, `C2_04_...`).

## Criterios de aceptación técnica

Un cambio se acepta en `main` solo si cumple **todos** estos criterios:

1. `python -m pytest` pasa completo.
2. `python -m pyflakes solicitudes tests app.py` no informa nada.
3. Todo cambio de comportamiento tiene un test nuevo y, si modifica un escenario grabado,
   la diferencia fue revisada y guardada en `docs/evidencias/`.
4. No se agregan `except:` genéricos ni `print`/`input` fuera de `consola.py`.
5. Ninguna función supera las 20 líneas ni los 4 parámetros.
6. El mensaje del commit explica qué cambia y por qué.

Estado al cerrar la revisión: los 6 criterios se cumplen (43 tests, `pyflakes` sin avisos).
Quedan abiertas O6, O7 y O8, documentadas como mejoras pendientes.
