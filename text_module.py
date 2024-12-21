import csv
from table_operations import infer_column_types

def load_table(file_path, infer_types=False):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        headers = next(reader)
        data = []
        for row in reader:
            data.append([None if cell == '' else cell for cell in row])

    if infer_types:
        column_types = infer_column_types(data)
        for i, row in enumerate(data):
            for col, col_type in column_types.items():
                if row[col] is not None:
                    row[col] = col_type(row[col])

    return headers, data

def save_table(file_path, headers, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(headers)
        writer.writerows([[cell if cell is not None else '' for cell in row] for row in data])
    print(f"Таблица сохранена в файл {file_path}")
