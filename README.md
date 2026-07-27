# Visualizador de Disponibilidad y Horarios de Facilitadores (INFOTEP)

Esta es una herramienta de alta fidelidad para procesar, visualizar y analizar la disponibilidad de fechas y horarios de los facilitadores a partir de los horarios oficiales generados por el sistema de Reporting Services de INFOTEP.

---

## 🚀 ¿Cómo actualizar los horarios de los facilitadores?

Para actualizar la base de datos o agregar nuevos facilitadores a la herramienta, simplemente sigue estos pasos:

1. **Sube el archivo PDF del facilitador** (por ejemplo, `Horario Ruth Uceta.pdf`) en la carpeta:
   ```bash
   horarios/
   ```
   *Puedes colocar todos los PDFs de facilitadores que desees analizar simultáneamente.*

2. **Ejecuta el script de procesamiento/parseo** para extraer y consolidar automáticamente todos los datos, horarios, materias, códigos y solapamientos:
   ```bash
   python3 parse_pdf.py
   ```
   Este comando regenerará automáticamente los archivos de base de datos del cliente:
   - `data.json` (Para consultas estructuradas en backend/APIs)
   - `data.js` (Cargado en caliente por el panel web)

3. **¡Listo!** Abre o refresca el visualizador interactivo:
   ```bash
   index.html
   ```

---

## 🎨 Características de la Herramienta de Visualización (`index.html`)

El panel de control cuenta con un diseño limpio, profesional e intuitivo (diseñado con Tailwind CSS) y ofrece las siguientes funcionalidades interactivas:

*   **Buscador y Selector de Facilitadores:** Permite buscar facilitadores de forma instantánea mediante un campo de texto y un selector dinámico para alternar su disponibilidad al instante.
*   **KPIs en Tiempo Real:** Muestra el número total de cursos/códigos asignados, total de horas lectivas, periodo de clases (desde el inicio al fin) y un desglose visual de las modalidades implicadas.
*   **Filtros Interactivos:** Filtra la agenda en tiempo real por:
    - **Modalidad:** Presencial, Virtual, Semipresencial.
    - **Código de Acción/Curso:** Carga códigos individuales o todos simultáneamente.
    - **Materia o Módulo:** Filtra clases por módulos específicos.
*   **Calendario Mensual Interactivo (FullCalendar):** Visualiza los días exactos y las horas de las clases. Haz clic en cualquier evento del calendario para ver un desglose completo de la materia, regional, horario semanal recurrente y modalidad.
*   **Matriz Semanal de Horarios (Heatmap):** Una representación consolidada de las horas en las que el facilitador tiene asignaciones recurrentes a lo largo de los días de la semana, marcando como "Disponible" las horas libres.
*   **Línea de Tiempo (Gantt Chart):** Permite ver en paralelo la duración (fechas de inicio y término) de cada materia asignada para identificar con facilidad la duración global del curso.
*   **Alertas Inteligentes de Solapamientos (Collisiones):** El sistema analiza todos los horarios recurrentes en las mismas fechas y muestra advertencias detalladas si el facilitador tiene clases colisionando en el mismo rango de hora y día de la semana.
