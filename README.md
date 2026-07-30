# Visualizador de Disponibilidad y Horarios de Facilitadores (INFOTEP)

Esta es una herramienta de alta fidelidad para procesar, visualizar y analizar la disponibilidad de fechas y horarios de los facilitadores a partir de los horarios oficiales generados por el sistema de Reporting Services de INFOTEP.

---

## ⚡️ Actualización de Horarios Interactiva (Automática)

Para que todos tus archivos nuevos se detecten y procesen al instante, hemos implementado un **Servidor de Desarrollo y Auto-Actualizador en Tiempo Real**:

1. **Inicia el servidor local** desde la terminal:
   ```bash
   python3 server.py
   ```
   *Esto iniciará un servidor web ligero y un vigilante en segundo plano (watcher) que escucha la carpeta `horarios/`.*

2. **Sube tus archivos PDF** a la carpeta:
   ```bash
   horarios/
   ```
   *En el momento en que guardes, elimines o edites cualquier archivo PDF en esta carpeta, el servidor detectará el cambio automáticamente y re-ejecutará el parser en milisegundos.*

3. **Visita la aplicación web** en tu navegador preferido:
   ```bash
   http://localhost:8000
   ```
   *Al refrescar o navegar, el visualizador cargará la base de datos totalmente actualizada con los nuevos facilitadores.*

---

## 🎨 Características de la Herramienta de Visualización (`index.html`)

El panel de control cuenta con un diseño limpio, profesional e intuitivo (diseñado con Tailwind CSS) y ofrece las siguientes funcionalidades interactivas:

*   **Buscador y Selector de Facilitadores:** Permite buscar facilitadores de forma instantánea mediante un campo de texto y un selector dinámico para alternar su disponibilidad al instante.
*   **KPIs en Tiempo Real:** Muestra el número total de cursos/códigos asignados, total de horas lectivas, periodo de clases (desde el inicio al fin) y un desglose visual de las modalidades implicadas.
*   **Filtros Interactivos:** Filtra la agenda en tiempo real por:
    - **Modalidad:** Presencial, Virtual, Semipresencial.
    - **Código de Acción/Curso:** Carga códigos individuales o todos simultáneamente.
    - **Materia o Módulo:** Filtra clases por módulos específicos.
*   **Boton "Ver Huecos / Horarios Disponibles" (NUEVO):** Al hacer clic, la matriz semanal de horarios (Heatmap) y el Calendario Mensual cambian de estado para resaltar en verde brillante y de forma clara exactamente **los bloques de tiempo libres (huecos de disponibilidad)** del facilitador para una asignación rápida de nuevas clases.
*   **Calendario Mensual Interactivo (FullCalendar):** Visualiza los días exactos y las horas de las clases. Haz clic en cualquier evento del calendario para ver un desglose completo de la materia, regional, horario semanal recurrente y modalidad.
*   **Matriz Semanal de Horarios (Heatmap):** Una representación consolidada de las horas en las que el facilitador tiene asignaciones recurrentes a lo largo de los días de la semana, marcando como "Disponible" las horas libres.
*   **Línea de Tiempo (Gantt Chart):** Permite ver en paralelo la duración (fechas de inicio y término) de cada materia asignada para identificar con facilidad la duración global del curso.
*   **Alertas Inteligentes de Solapamientos (Collisiones):** El sistema analiza todos los horarios recurrentes en las mismas fechas y muestra advertencias detalladas si el facilitador tiene clases colisionando en el mismo rango de hora y día de la semana.
