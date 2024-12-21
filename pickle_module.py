import pickle
import os
from table_operations import infer_column_types

def save_table(file_path, headers, data, max_rows=None):
    table = {'headers': headers, 'data': data}
    with open(file_path, 'wb') as file:
        pickle.dump(table, file)
    print(f"Таблица сохранена в файл {file_path}")

def load_table(file_path, *additional_files, infer_types=False):
    headers = None
    data = []
    current_id = 0

    files = [file_path] + list(additional_files)

    for file in files:
        with open(file, 'rb') as f:
            table = pickle.load(f)
            current_headers = table.get('headers', [])
            current_data = table.get('data', [])
            if headers is None:
                headers = current_headers
            elif headers != current_headers:
                raise ValueError(f"Структура столбцов файла {file} не соответствует структуре столбцов первого файла.")
            for row in current_data:
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
    table = {'headers': headers, 'data': data}
    with open(file_path, 'wb') as file:
        pickle.dump(table, file)
    print(f"Объединенная таблица сохранена в файл {file_path}")
