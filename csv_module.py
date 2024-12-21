import csv
import os
from table_operations import infer_column_types

def save_table(file_path, headers, data, max_rows=None):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow([cell if cell is not None else '' for cell in row])
    print(f"Таблица сохранена в файл {file_path}")

def load_table(file_path, *additional_files, infer_types=False):
    headers = None
    data = []
    current_id = 0

    files = [file_path] + list(additional_files)

    for file in files:
        with open(file, 'r', newline='') as f:
            reader = csv.reader(f)
            current_headers = next(reader)
            if headers is None:
                headers = current_headers
            elif headers != current_headers:
                raise ValueError(f"Структура столбцов файла {file} не соответствует структуре столбцов первого файла.")
            for row in reader:
                current_id += 1
                data.append([str(current_id)] + row[1:])  # Удаляем старый ID и добавляем новый

    if infer_types:
        column_types = infer_column_types(data)
        for i, row in enumerate(data):
            for col, col_type in column_types.items():
                if row[col] is not None:
                    row[col] = col_type(row[col])

    return headers, data

def save_combined_table(file_path, headers, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows([[cell if cell is not None else '' for cell in row] for row in data])
    print(f"Объединенная таблица сохранена в файл {file_path}")
