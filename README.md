# Sistema de Gestión de Solicitudes Académicas

Aplicación de consola en Python para registrar y seguir solicitudes de estudiantes
(certificados, equivalencias, cambios de comisión y reclamos de nota).

## Funcionalidades
1. Registrar solicitud (estudiante, tipo, descripción, prioridad).
2. Cambiar estado (PENDIENTE → EN PROCESO → RESUELTA / RECHAZADA).
3. Asignar responsable (catálogo de responsables por área).
4. Buscar / filtrar por estado, tipo o legajo.
5. Reporte básico (totales por estado y tipo, pendientes de prioridad alta).

## Requisitos y uso
- Python 3.10 o superior. Sin dependencias externas.

```bash
python app.py
```

Los datos se guardan en `datos.json` en la carpeta desde donde se ejecuta.

## Tecnologías
- Python 3 (biblioteca estándar: `json`, `datetime`).
- Persistencia en archivo JSON.
