# LIGA ANTIGUOS ALUMNOS RETAMAR

## Explicación del Script

Este proyecto contiene un script de Python (`LigaRetamar.py`) que procesa el calendario de la Liga de Antiguos Alumnos de Retamar. Esto es lo que hace el script:

1. Lee un archivo Excel que contiene el calendario de la liga.
2. Procesa los datos del calendario, extrayendo información sobre partidos, equipos, divisiones y fechas.
3. Crea archivos iCalendar (.ics) para:
   - El calendario completo de la liga
   - Calendarios individuales de cada equipo
   - Calendarios específicos de cada división

## Estructura de Carpetas

- `Equipos/`: Esta carpeta contiene archivos iCalendar individuales para cada equipo de la liga. Cada archivo incluye todos los partidos de ese equipo específico.
- `Divisiones/`: Esta carpeta contiene archivos iCalendar para cada división de la liga. Cada archivo incluye todos los partidos dentro de esa división.

## Uso

Para utilizar el script, asegúrate de tener instaladas las dependencias necesarias y ejecuta el archivo `LigaRetamar.py`. El script generará los archivos iCalendar en las carpetas correspondientes basándose en el archivo Excel de entrada.
