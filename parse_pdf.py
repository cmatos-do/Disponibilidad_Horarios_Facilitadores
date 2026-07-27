import pypdf
import re
import json

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

def extract_rows_from_all_pages(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    all_rows = []

    facilitator_name = "RUTH ADIBELL UCETA PACHECO"
    facilitator_doc = "402-2306995-2"

    for p_idx, page in enumerate(reader.pages):
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
        for y in sorted_ys:
            row_items = sorted(rows_dict[y], key=lambda e: e['x'])
            all_rows.append({
                'page': p_idx + 1,
                'y': y,
                'items': row_items
            })

    return facilitator_name, facilitator_doc, all_rows

def parse_schedule(pdf_path):
    fac_name, fac_doc, rows = extract_rows_from_all_pages(pdf_path)

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

            # clean duplicates or wraps
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
        'facilitator_name': fac_name,
        'facilitator_doc': fac_doc,
        'courses': [c for c in courses if c['code'] and c['schedules']]
    }

if __name__ == '__main__':
    parsed_data = parse_schedule('Horario Ruth Uceta.pdf')

    # Save as JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    # Save as JS for client side
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('const SCHEDULE_DATA = ')
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        f.write(';\n')

    print('Successfully parsed and generated data.json and data.js!')
