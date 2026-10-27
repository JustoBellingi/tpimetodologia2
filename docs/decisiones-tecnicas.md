# Decisiones técnicas del refactoring

## 1. Red de seguridad antes de tocar el código
Antes de refactorizar se grabaron 5 escenarios de uso sobre la versión inicial
(`tests/caracterizacion`). Cada test ejecuta `app.py` como lo haría un usuario y compara
la salida por pantalla y el `datos.json` final contra lo grabado.
Si un refactoring cambia un solo carácter visible, el test falla.

## 2. Refactorizar en pasos chicos y siempre en verde
Se construyó la arquitectura nueva al lado de la vieja (`solicitudes/`) y recién en el
último paso `app.py` pasó a delegar en ella. Todos los commits de refactoring pasan
la suite completa en un checkout limpio.

## 3. Mantener el formato de `datos.json`
Los nombres internos mejoraron (`nombre`, `legajo`), pero el archivo conserva las claves
históricas (`nom`, `leg`, `est`...). `RepositorioJSON` traduce entre ambos.
Motivo: un usuario con datos guardados por la versión inicial no debe perderlos.

## 4. Errores con excepciones, mensajes en un solo lugar
El dominio lanza excepciones (`DatosInvalidos`, `TransicionInvalida`...). Solo la consola
las convierte en texto `Error: ...`. Los errores inesperados ya no se silencian.

## 5. Cambios de comportamiento intencionales (mejoras)
| Situación | Versión inicial | Versión refactorizada |
|---|---|---|
| ID no numérico | `Ocurrio un error` | `Error: el ID debe ser numerico` |
| Fin de entrada (EOF) en el menú | Traceback de Python | `Hasta luego` y sale |
| Error de programación inesperado | Oculto por `except:` | Se muestra (no se silencia) |

## 6. Mejoras pendientes (fuera de alcance)
- Si `datos.json` está dañado se sigue arrancando vacío (igual que antes); lo correcto
  sería avisar y no sobrescribir el archivo. Se dejó igual para no cambiar el comportamiento.
- El catálogo de responsables sigue fijo en código.
