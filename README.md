# Sistema de Gestión de Solicitudes Académicas

Aplicación de consola en Python para registrar y seguir solicitudes de estudiantes
(certificados, equivalencias, cambios de comisión y reclamos de nota).
Trabajo Práctico Integrador de Metodología de Sistemas II: el foco está en diagnosticar
y refactorizar una versión inicial con deuda técnica, sin cambiar su comportamiento externo.

## Funcionalidades
1. Registrar solicitud (estudiante, tipo, descripción, prioridad).
2. Cambiar estado (PENDIENTE → EN PROCESO → RESUELTA / RECHAZADA).
3. Asignar responsable (catálogo de responsables por área).
4. Buscar / filtrar por estado, tipo o legajo.
5. Reporte básico (totales por estado y tipo, pendientes de prioridad alta).

## Instalación y uso
Requiere Python 3.10 o superior. La aplicación no tiene dependencias externas.

```bash
python app.py                     # ejecutar el sistema
pip install pytest                # solo para correr los tests
python -m pytest                  # 37 tests: caracterización + unitarios
```

Los datos se guardan en `datos.json` en la carpeta desde donde se ejecuta.

## Estructura
```
app.py                    punto de entrada
solicitudes/
  dominio.py              entidades, enums y reglas de negocio
  formulario.py           validación de datos de alta (Parameter Object)
  repositorio.py          persistencia JSON / memoria detrás de una interfaz
  filtros.py              criterios de búsqueda polimórficos
  servicio.py             casos de uso y reporte
  consola.py              menú, lectura y mensajes
  main.py                 armado de dependencias
tests/
  caracterizacion/        golden master grabado sobre la versión inicial
  unitarios/              tests de dominio, formulario, servicio y consola
docs/                     diagnóstico y decisiones técnicas
```

## Tags del repositorio
| Tag | Contenido |
|---|---|
| `estado-inicial` | Versión inicial con deuda técnica (un solo archivo `app.py`) |
| `etapa-diagnostico` | Diagnóstico de code smells + tests de caracterización |
| `etapa-refactoring` | Refactorings aplicados, todos los tests en verde |

## Tecnologías
- Python 3 (biblioteca estándar: `json`, `dataclasses`, `enum`, `typing`, `pathlib`).
- Persistencia en archivo JSON.
- `pytest` para pruebas.
