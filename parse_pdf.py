import pypdf
import re
import json
import os

X_COLUMNS = {
    16.42: 'materia',
    211.46: 'start_date',
    303.48: 'end_date',
    420.70: 'Lunes',
    490.46: 'Martes',
    560.16: 'Miércoles',
    629.93: 'Jueves',
    699.62: 'Viernes',
    769.39: 'Sábado',
    839.09: 'Domingo',
    946.1: 'horas',
    951.6: 'horas',
    961.2: 'impartir'
}

DAYS_ORDER = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

def get_column_by_x(x):
    best_col = None
    min_diff = 12.0
    for col_x, col_name in X_COLUMNS.items():
        diff = abs(x - col_x)
        if diff < min_diff:
            min_diff = diff
            best_col = col_name
    return best_col

def extract_rows_from_page(page, p_idx):
    elements = []
    def visitor(text, cm, tm, fontDict, fontSize):
        t = text.strip()
        if t:
            elements.append({
                'text': t,
                'x': tm[4],
                'y': tm[5],
                'h': fontSize
            })
    page.extract_text(visitor_text=visitor)

    rows_dict = {}
    for el in elements:
        found = False
        for y_key in rows_dict:
            if abs(el['y'] - y_key) < 4.0:
                rows_dict[y_key].append(el)
                found = True
                break
        if not found:
            rows_dict[el['y']] = [el]

    sorted_ys = sorted(rows_dict.keys(), reverse=True)
    page_rows = []
    for y in sorted_ys:
        row_items = sorted(rows_dict[y], key=lambda e: e['x'])
        page_rows.append({
            'page': p_idx + 1,
            'y': y,
            'items': row_items
        })
    return page_rows

def parse_single_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)

    # Extract general Facilitator name and document
    # Search first few pages for Name and Doc
    facilitator_name = "Desconocido"
    facilitator_doc = "Desconocido"

    all_text = ""
    for page in reader.pages:
        all_text += page.extract_text() + "\n"

    doc_match = re.search(r'Documento:\s*([\d-]+)', all_text)
    name_match = re.search(r'Nombre:\s*(.*?)\s*Código:', all_text, re.DOTALL)

    if doc_match:
        facilitator_doc = doc_match.group(1).strip()
    if name_match:
        facilitator_name = name_match.group(1).strip().replace('\n', ' ')

    # Extract page elements
    rows = []
    for p_idx, page in enumerate(reader.pages):
        rows.extend(extract_rows_from_page(page, p_idx))

    courses = []
    current_course = None

    i = 0
    while i < len(rows):
        row = rows[i]
        items = row['items']

        has_codigo = any('Código:' in item['text'] for item in items)
        if has_codigo:
            # course block found
            course_meta_items = []
            while i < len(rows):
                has_headers = any(h in rows[i]['items'][0]['text'] for h in ['Materia', 'Fecha Inicio', 'Fecha Término'] if rows[i]['items'])
                if has_headers:
                    break
                course_meta_items.extend(rows[i]['items'])
                i += 1

            code = ""
            salida_parts = []
            modalidad_parts = []
            regional_parts = []

            j = 0
            while j < len(course_meta_items):
                txt = course_meta_items[j]['text']
                if 'Código:' in txt:
                    if j + 1 < len(course_meta_items) and course_meta_items[j+1]['text'].isdigit():
                        code = course_meta_items[j+1]['text']
                        j += 2
                        continue
                elif 'Salida:' in txt:
                    j += 1
                    while j < len(course_meta_items) and 'Modalidad:' not in course_meta_items[j]['text']:
                        salida_parts.append(course_meta_items[j]['text'])
                        j += 1
                    continue
                elif 'Modalidad:' in txt:
                    j += 1
                    while j < len(course_meta_items) and 'Regional:' not in course_meta_items[j]['text']:
                        modalidad_parts.append(course_meta_items[j]['text'])
                        j += 1
                    continue
                elif 'Regional:' in txt:
                    j += 1
                    while j < len(course_meta_items) and 'Materia' not in course_meta_items[j]['text'] and 'Código:' not in course_meta_items[j]['text']:
                        regional_parts.append(course_meta_items[j]['text'])
                        j += 1
                    continue
                j += 1

            salida = " ".join(salida_parts).strip()
            modalidad = " ".join(modalidad_parts).strip()
            regional = " ".join(regional_parts).strip()

            salida = re.sub(r'\s+', ' ', salida)
            modalidad = re.sub(r'\s+', ' ', modalidad)
            regional = re.sub(r'\s+', ' ', regional)

            current_course = {
                'code': code,
                'salida': salida,
                'modalidad': modalidad,
                'regional': regional,
                'schedules': []
            }
            courses.append(current_course)

        if current_course and len(items) >= 4:
            has_dates = False
            start_date_str = ""
            end_date_str = ""
            materia = ""
            horas = ""
            impartir = ""
            days_schedule = {}

            for item in items:
                col = get_column_by_x(item['x'])
                txt = item['text']
                if col == 'materia':
                    materia = txt
                elif col == 'start_date' and re.match(r'^\d{2}/\d{2}/\d{4}$', txt):
                    start_date_str = txt
                    has_dates = True
                elif col == 'end_date' and re.match(r'^\d{2}/\d{2}/\d{4}$', txt):
                    end_date_str = txt
                elif col in DAYS_ORDER:
                    if '-' in txt and len(txt) >= 11:
                        days_schedule[col] = txt
                elif col == 'horas':
                    horas = txt
                elif col == 'impartir':
                    impartir = txt

            if has_dates and impartir in ['Presencial', 'Virtual', 'Semipresencial']:
                current_course['schedules'].append({
                    'materia': materia,
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'days': days_schedule,
                    'hours': int(horas) if horas.isdigit() else horas,
                    'modality': impartir
                })

        i += 1

    return {
        'facilitator_name': facilitator_name,
        'facilitator_doc': facilitator_doc,
        'courses': [c for c in courses if c['code'] and c['schedules']]
    }

def main():
    horarios_dir = 'horarios'
    facilitators_dict = {}

    if os.path.exists(horarios_dir):
        pdf_files = []
        for root, dirs, files in os.walk(horarios_dir):
            for filename in files:
                if filename.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, filename))
        print(f"Found PDF files: {pdf_files}")
        for pdf_path in pdf_files:
            try:
                data = parse_single_pdf(pdf_path)
                key = data['facilitator_doc'] if data['facilitator_doc'] != "Desconocido" else data['facilitator_name']
                if key in facilitators_dict:
                    existing_courses = facilitators_dict[key]['courses']
                    for new_course in data['courses']:
                        existing_course = next((c for c in existing_courses if c['code'] == new_course['code']), None)
                        if existing_course:
                            for new_sched in new_course['schedules']:
                                dup = False
                                for ext_sched in existing_course['schedules']:
                                    if ext_sched['materia'] == new_sched['materia'] and ext_sched['start_date'] == new_sched['start_date'] and ext_sched['end_date'] == new_sched['end_date']:
                                        dup = True
                                        break
                                if not dup:
                                    existing_course['schedules'].append(new_sched)
                        else:
                            existing_courses.append(new_course)
                else:
                    facilitators_dict[key] = data
                print(f"Successfully parsed {pdf_path} ({data['facilitator_name']})")
            except Exception as e:
                print(f"Error parsing {pdf_path}: {e}")

    output_schema = {
        'facilitators': list(facilitators_dict.values())
    }

    # Save as JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output_schema, f, indent=2, ensure_ascii=False)

    # Save as JS for client side
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('const SCHEDULE_DATABASE = ')
        json.dump(output_schema, f, indent=2, ensure_ascii=False)
        f.write(';\n')

    print('Multi-facilitator database saved successfully!')

if __name__ == '__main__':
    main()
