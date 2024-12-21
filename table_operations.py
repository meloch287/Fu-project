class Table:
    def __init__(self, headers, data):
        self.headers = headers
        self.data = data
        self.column_types = {}

    def get_rows_by_number(self, start, stop=None, copy_table=False):
        if stop is None:
            stop = start + 1
        rows = self.data[start:stop]
        if copy_table:
            return Table(self.headers, rows)
        return rows

    def get_rows_by_index(self, *vals, copy_table=False):
        rows = [row for row in self.data if row[0] in vals]
        if copy_table:
            return Table(self.headers, rows)
        return rows

    def get_column_types(self, by_number=True):
        column_types = {}
        for i, header in enumerate(self.headers):
            column_data = [row[i] for row in self.data]
            column_type = type(column_data[0]) if column_data and column_data[0] is not None else str
            column_types[i if by_number else header] = column_type
        return column_types

    def set_column_types(self, types_dict, by_number=True):
        for key, value_type in types_dict.items():
            column_index = key if by_number else self.headers.index(key)
            for row in self.data:
                if row[column_index] is not None:
                    row[column_index] = value_type(row[column_index])

    def get_values(self, column):
        column_index = self._get_column_index(column)
        return [self._cast_value(row[column_index], column_index) for row in self.data]

    def get_value(self, column):
        column_index = self._get_column_index(column)
        if len(self.data) == 0:
            raise ValueError("Table is empty")
        return self._cast_value(self.data[0][column_index], column_index)

    def set_values(self, values, column):
        column_index = self._get_column_index(column)
        for i, value in enumerate(values):
            self.data[i][column_index] = self._cast_value(value, column_index)

    def set_value(self, row_index, column, value):
        column_index = self._get_column_index(column)
        if row_index < 0 or row_index >= len(self.data):
            raise ValueError("Invalid row index")
        self.data[row_index][column_index] = self._cast_value(value, column_index)

    def print_table(self):
        print('\t'.join(self.headers))
        for row in self.data:
            print('\t'.join(map(lambda x: '' if x is None else str(x), row)))

    def _cast_value(self, value, column):
        column_type = self.column_types.get(column, str)
        return column_type(value) if value is not None else None

    def _get_column_index(self, column):
        if isinstance(column, int):
            return column
        elif isinstance(column, str):
            if column.isdigit():
                return int(column)
            else:
                return self.headers.index(column)
        else:
            raise ValueError("Column must be an integer or a string")

    def split_table_by_row(self, row_number):
        if row_number < 0 or row_number >= len(self.data):
            raise ValueError("Invalid row number")
        top_half = self.data[:row_number]
        bottom_half = self.data[row_number:]
        return Table(self.headers, top_half), Table(self.headers, bottom_half)

    def apply_operation(self):
        operation = input("Выберите операцию (умножить/разделить/сложить/вычесть): ").strip().lower()
        if operation not in ["умножить", "разделить", "сложить", "вычесть"]:
            raise ValueError("Неверная операция")

        target = input("Выберите цель (строки/столбцы): ").strip().lower()
        if target not in ["строки", "столбцы"]:
            raise ValueError("Неверная цель")

        if target == "строки":
            row_index = int(input("Введите номер строки: ")) - 1  # Вычитаем 1, чтобы соответствовать индексам Python
            if row_index < 0 or row_index >= len(self.data):
                raise ValueError("Неверный номер строки")
            value = float(input("Введите число для операции: "))
            for i in range(len(self.data[row_index])):
                if isinstance(self.data[row_index][i], (int, float)):
                    if operation == "умножить":
                        self.data[row_index][i] *= value
                    elif operation == "разделить":
                        self.data[row_index][i] /= value
                    elif operation == "сложить":
                        self.data[row_index][i] += value
                    elif operation == "вычесть":
                        self.data[row_index][i] -= value

        elif target == "столбцы":
            column_index = self._get_column_index(input("Введите номер или имя столбца: "))
            value = float(input("Введите число для операции: "))
            for row in self.data:
                if isinstance(row[column_index], (int, float)):
                    if operation == "умножить":
                        row[column_index] *= value
                    elif operation == "разделить":
                        row[column_index] /= value
                    elif operation == "сложить":
                        row[column_index] += value
                    elif operation == "вычесть":
                        row[column_index] -= value

    def compare_columns(self, operation):
        column1 = self._get_column_index(input("Введите номер или имя первого столбца: "))
        column2 = self._get_column_index(input("Введите номер или имя второго столбца: "))
        bool_list = []
        for row in self.data:
            if isinstance(row[column1], (int, float)) and isinstance(row[column2], (int, float)):
                if operation == "==":
                    bool_list.append(row[column1] == row[column2])
                elif operation == ">":
                    bool_list.append(row[column1] > row[column2])
                elif operation == "<":
                    bool_list.append(row[column1] < row[column2])
                elif operation == ">=":
                    bool_list.append(row[column1] >= row[column2])
                elif operation == "<=":
                    bool_list.append(row[column1] <= row[column2])
                elif operation == "!=":
                    bool_list.append(row[column1] != row[column2])
            else:
                bool_list.append(False)
        return bool_list

    def filter_rows(self, bool_list, copy_table=False):
        if len(bool_list) != len(self.data):
            raise ValueError("Длина bool_list должна соответствовать количеству строк в таблице")
        filtered_data = [row for i, row in enumerate(self.data) if bool_list[i]]
        if copy_table:
            return Table(self.headers, filtered_data)
        self.data = filtered_data

def infer_column_types(data):
    column_types = {}
    for i in range(len(data[0])):
        column_data = [row[i] for row in data if row[i] is not None]
        if not column_data:
            column_types[i] = str
            continue
        try:
            int_values = [int(value) for value in column_data]
            column_types[i] = int
        except ValueError:
            try:
                float_values = [float(value) for value in column_data]
                column_types[i] = float
            except ValueError:
                column_types[i] = str
    print("Определенные типы столбцов:", column_types)  # Вывод типов столбцов для отладки
    return column_types

def merge_tables(table1, table2, by_number=True, conflict_resolution='first'):
    """
    Объединяет две таблицы по номеру строки или по индексу.

    :param table1: Первая таблица (объект Table).
    :param table2: Вторая таблица (объект Table).
    :param by_number: Флаг, указывающий, объединять ли таблицы по номеру строки (True) или по индексу (False).
    :param conflict_resolution: Способ разрешения конфликтов ('first' или 'second').
    :return: Объединенная таблица (объект Table).
    """
    headers1 = table1.headers
    headers2 = table2.headers
    data1 = table1.data
    data2 = table2.data

    # Объединяем заголовки
    combined_headers = list(set(headers1) | set(headers2))

    # Создаем словари для быстрого доступа к индексам столбцов
    headers1_index = {header: i for i, header in enumerate(headers1)}
    headers2_index = {header: i for i, header in enumerate(headers2)}

    # Объединяем данные
    combined_data = []
    if by_number:
        max_len = max(len(data1), len(data2))
        for i in range(max_len):
            row1 = data1[i] if i < len(data1) else [None] * len(headers1)
            row2 = data2[i] if i < len(data2) else [None] * len(headers2)
            combined_row = []
            for header in combined_headers:
                value1 = row1[headers1_index[header]] if header in headers1_index else None
                value2 = row2[headers2_index[header]] if header in headers2_index else None
                if value1 is not None and value2 is not None and value1 != value2:
                    if conflict_resolution == 'first':
                        combined_row.append(value1)
                    elif conflict_resolution == 'second':
                        combined_row.append(value2)
                    else:
                        raise ValueError(f"Конфликт значений в столбце {header} для строки {i}")
                else:
                    combined_row.append(value1 if value1 is not None else value2)
            combined_data.append(combined_row)
    else:
        index_set = set(row[0] for row in data1) | set(row[0] for row in data2)
        for index in index_set:
            row1 = next((row for row in data1 if row[0] == index), [None] * len(headers1))
            row2 = next((row for row in data2 if row[0] == index), [None] * len(headers2))
            combined_row = []
            for header in combined_headers:
                value1 = row1[headers1_index[header]] if header in headers1_index else None
                value2 = row2[headers2_index[header]] if header in headers2_index else None
                if value1 is not None and value2 is not None and value1 != value2:
                    if conflict_resolution == 'first':
                        combined_row.append(value1)
                    elif conflict_resolution == 'second':
                        combined_row.append(value2)
                    else:
                        raise ValueError(f"Конфликт значений в столбце {header} для индекса {index}")
                else:
                    combined_row.append(value1 if value1 is not None else value2)
            combined_data.append(combined_row)

    return Table(combined_headers, combined_data)
