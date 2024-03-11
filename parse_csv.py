import csv
import sys
import json
import re

def process_part(part):
    file = open(f'part{part}.csv', 'r')
    text = file.read()
    text = text.replace('Module Pin', 'Module Pin,')
    text = text.replace('Module pin', 'Module Pin,')
    text = text.replace('Pad Name', 'Pad Name,')
    text = text.replace('Signal Name', 'Signal Name,')
    file.close()
    file = open(f'part{part}.csv', 'w')
    file.write(text)
    file.close()
    file = open(f'part{part}.csv', 'r')
    reader = csv.reader(file)
    rows = list(reader)
    for row in rows:
        if (len(row) == 4 or len(row) == 5) and re.match(r'^[A-Z0-9_\s]+$', row[0]):
            if '\n' in row[0]:
                print(f'part{part}A {row}')
                row[0] = row[0].replace('\n', '')
    tables = []
    table_type = 0
    current_table = []
    for i, row in enumerate(rows):
        if row.count('Name') == 1 and row.count('Offset') == 1 and row.count('Size') == 1:
            if current_table:
                tables.append((table_type, current_table))
            current_table = [row]
            table_type = 1
        elif row.count('Bit') == 1 and row.count('Attr') == 1:
            if rows[i-1].count('Bit') == 1 and rows[i-1].count('Attr') == 1:
                continue
            if current_table:
                tables.append((table_type, current_table))
            table_type = 2
            current_table = [row]
        else:
            if table_type == 1 and len(row) == 5:
                if ' ' in row[0] or '\n' in row[0]:
                    print(f'part{part} {row}')
                if ' ' in row[0] or '\n' in row[0]:
                    current_table = []
                    table_type = 0
                    continue
                current_table.append(row)
            elif table_type == 2 and len(row) == 4:
                current_table.append(row)
            else:
                if current_table:
                    tables.append((table_type, current_table))
                    current_table = []
                    table_type = 0
    if current_table:
        tables.append((table_type, current_table))
        current_table = []
        table_type = 0
    new_tables = []
    for i in range(len(tables)):
        ttype, table = tables[i]
        if len(table) == 1:
            continue
        if ttype == 2 and i > 0 and tables[i - 1][0] == 2 and len(table) > 1 and len(tables[i - 1][1]) > 1:
            if int(table[1][0].split(':')[0]) == int(tables[i - 1][1][-1][0].split(':')[-1]) - 1:
                for row in table[1:]:
                    new_tables[-1][1].append(row)
                continue
        if ttype == 1 and i > 0 and tables[i - 1][0] == 1 and len(table) > 1 and len(tables[i - 1][1]) > 1:
            for row in table[1:]:
                new_tables[-1][1].append(row)
            continue
        new_tables.append((ttype, table.copy()))


    html = '''
    <style>
        table {
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 5px;
        }
    </style>
    '''
    descriptions = json.load(open(f'part{part}_descriptions.json'))
    j = 0
    final_data = []
    regno = 0
    for type, table in new_tables:
        if type == 2:
            name = final_data[-1]['summary'][regno]['name']
            offset = final_data[-1]['summary'][regno]['offset']
            size = final_data[-1]['summary'][regno]['size']
            reset = final_data[-1]['summary'][regno]['reset']
            description = final_data[-1]['summary'][regno]['description']
            if final_data[-1]['summary'][regno]['name'] not in descriptions[j]:
                if 'DMAC' in descriptions[j]:
                    name = descriptions[j].split('\n')[0]
                    offset = re.search(r'0x[0-9A-Fa-f]+', descriptions[j]).group(0)
                    size = "W"
                    reset = "0x00000000"
                    description = descriptions[j].split('\n')[-1]
                else:
                    print(f'part{part} Anomaly {final_data[-1]["summary"][regno]["name"]}')
            html += f'<p><b>' + name + '<br>Offset: ' + offset + '<br>Description: ' + description.replace("\n", "<br>") + '</b></p>\n'
            final_data[-1]['registers'].append({
                'type': 'register',
                'name': name,
                'offset': offset,
                'size': size,
                'reset': reset,
                'bit_ranges': [{
                    'name': x[3].split('\n')[0].upper() if final_data[-1]['name'] not in ["DMAC"] or x[3].strip().lower() == 'reserved' or ('_' in x[3].split('\n')[0] and ' ' not in x[3].split('\n')[0]) else '',
                    'bit_range': x[0],
                    'attr': x[1].replace(' ', '').replace('\n', ''),
                    'reset': x[2].replace(' ', ''),
                    'description': '\n'.join(x[3].split('\n')[1:]) if len(x[3].split('\n')) > 1 and final_data[-1]['name'] not in ["DMAC"] else x[3],
                } for x in table[1:]],
                'description': description
            })
            j += 1
            regno += 1
        else:
            regno = 0
            if final_data:
                if len(final_data[-1]['summary']) != len(final_data[-1]['registers']):
                    print(f'part{part} {final_data[-1]["summary"][0]["name"]}')
            if any(' ' in x[0] or '\n' in x[0] for x in table[1:]):
                print(f'part{part} Summary {table[1]}')
                continue
            final_data.append({
                'type': 'group',
                'registers': [],
                'name': table[1][0].split('_')[0],
                'summary': [{
                    'name': x[0].replace('\n', ''),
                    'offset': x[1],
                    'size': x[2],
                    'reset': x[3],
                    'description': x[4].replace('\n', ' ')
                } for x in table[1:]]
            })
            html += f'<p><b>' + table[1][0].split('_')[0] + ' Registers Summary</b></p>\n'
        html += '<table>\n'
        for i, row in enumerate(table):
            html += '  <tr>\n'
            for cell in row:
                cell = cell.replace('W  O', 'WO')
                cell = cell.replace('R  O', 'RO')
                cell = cell.replace('R  W', 'RW')
                cell = cell.replace('W1\nC', 'W1C')
                cell = cell.replace('0 x', '0x')
                cell = cell.replace(' ', '&nbsp;')
                cell = cell.replace('\n', '<br>')
                if i == 0:
                    html += f'    <th>{cell}</th>\n'
                else:
                    html += f'    <td>{cell}</td>\n'
            html += '  </tr>\n'
        html += '</table>\n'
        html += '<br><br>\n'
    with open(f'part{part}.html', 'w') as f:
        f.write(html)

    json.dump(final_data, open(f'part{part}_final.json', 'w'), indent=2)

if __name__ == '__main__':
    process_part(sys.argv[1])
