import os
import tkinter as tk
from tkinter import filedialog
import logging
from csv_module import load_table as load_csv, save_table as save_csv, save_combined_table as save_combined_csv
from pickle_module import load_table as load_pickle, save_table as save_pickle, save_combined_table as save_combined_pickle
from text_module import load_table as load_text, save_table as save_text
from table_operations import Table, infer_column_types, merge_tables  # Импортируем merge_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def user_choice(path):
    files = []
    try:
        for file in os.listdir(path):
            if file.endswith(".txt") or file.endswith(".csv") or file.endswith(".pickle"):
                files.append((file, os.path.join(path, file)))
    except OSError as e:
        logger.error(f"Ошибка при чтении директории: {e}")
    return files

def main():
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно tkinter
    try:
        path = filedialog.askdirectory(title="Выберите папку")
        if not path:
            logger.info("Путь к папке не выбран.")
            return
    except tk.TclError as e:
        logger.error(f"Ошибка при выборе директории: {e}")
        return

    while True:
        files = user_choice(path)
        if not files:
            logger.info("Нет подходящих файлов в выбранной папке.")
            return

        print("Найденные файлы:")
        for i, (file_name, file_path) in enumerate(files, start=1):
            print(f"{i}. {file_name}")

        try:
            file_indices = input("Введите номера файлов через пробел: ").split()
            file_indices = [int(index) - 1 for index in file_indices]
            if any(index < 0 or index >= len(files) for index in file_indices):
                logger.error("Неверные номера файлов.")
                continue
        except ValueError:
            logger.error("Неверный ввод. Пожалуйста, введите числа через пробел.")
            continue

        selected_files = [files[i] for i in file_indices]
        action = input("1. Выгрузить таблицу\n2. Сохранить таблицу\n3. Объединить таблицы\n")
        if action == "1":
            try:
                file_paths = [file_path for _, file_path in selected_files]
                infer_types = input("Автоматически определить типы столбцов? (да/нет): ").strip().lower() == "да"
                if len(file_paths) > 1:
                    if selected_files[0][0].endswith(".csv"):
                        headers, table_data = load_csv(*file_paths, infer_types=infer_types)
                    elif selected_files[0][0].endswith(".pickle"):
                        headers, table_data = load_pickle(*file_paths, infer_types=infer_types)
                    else:
                        logger.error("Неподдерживаемый формат файла для загрузки.")
                        continue
                else:
                    if selected_files[0][0].endswith(".csv"):
                        headers, table_data = load_csv(file_paths[0], infer_types=infer_types)
                    elif selected_files[0][0].endswith(".pickle"):
                        headers, table_data = load_pickle(file_paths[0], infer_types=infer_types)
                    elif selected_files[0][0].endswith(".txt"):
                        headers, table_data = load_text(file_paths[0], infer_types=infer_types)
                    else:
                        logger.error("Неподдерживаемый формат файла для загрузки.")
                        continue
            except Exception as e:
                logger.error(f"Ошибка при загрузке файла: {e}")
                continue

            table = Table(headers, table_data)
            if infer_types:
                logger.info("Типы столбцов после загрузки:")
                logger.info(infer_column_types(table_data))

            while True:
                print("\nВыберите операцию для выгрузки:")
                print("1. Получить строки по номеру")
                print("2. Получить строки по индексу")
                print("3. Получить типы столбцов")
                print("4. Установить типы столбцов")
                print("5. Получить значения из столбца")
                print("6. Получить одно значение из столбца")
                print("7. Установить значения в столбец")
                print("8. Установить одно значение в столбец")
                print("9. Выгрузить всю таблицу")
                print("10. Разделить таблицу по номеру строки")
                print("11. Применить арифметическую операцию")
                print("12. Применить операцию сравнения")
                print("13. Фильтровать строки")
                print("14. Выйти")

                operation = input("Введите номер операции: ")

                try:
                    if operation == "1":
                        start = int(input("Введите начальный номер строки: "))
                        stop = int(input("Введите конечный номер строки: "))
                        if start < 0 or stop > len(table.data):
                            raise ValueError("Неверный диапазон строк.")
                        copy_table = input("Копировать таблицу? (да/нет): ").lower() == "да"
                        result = table.get_rows_by_number(start, stop, copy_table)
                        print("Результат:")
                        result.print_table()

                    elif operation == "2":
                        vals = input("Введите значения для индексации через пробел: ").split()
                        if not vals:
                            raise ValueError("Нет значений для индексации.")
                        copy_table = input("Копировать таблицу? (да/нет): ").lower() == "да"
                        result = table.get_rows_by_index(*vals, copy_table=copy_table)
                        print("Результат:")
                        result.print_table()

                    elif operation == "3":
                        by_number = input("Использовать индексы столбцов? (да/нет): ").lower() == "да"
                        result = table.get_column_types(by_number)
                        print("Типы столбцов:", result)

                    elif operation == "4":
                        types_dict = eval(input("Введите словарь типов столбцов (например, {0: int, 1: float}): "))
                        if not isinstance(types_dict, dict):
                            raise ValueError("Неверный формат словаря типов столбцов.")
                        by_number = input("Использовать индексы столбцов? (да/нет): ").lower() == "да"
                        table.set_column_types(types_dict, by_number)
                        print("Типы столбцов установлены.")

                    elif operation == "5":
                        column = input("Введите номер или имя столбца: ")
                        result = table.get_values(column)
                        print("Значения из столбца:", result)

                    elif operation == "6":
                        column = input("Введите номер или имя столбца: ")
                        result = table.get_value(column)
                        print("Значение из столбца:", result)

                    elif operation == "7":
                        values = input("Введите значения через пробел: ").split()
                        if len(values) != len(table.data):
                            raise ValueError("Количество значений не соответствует количеству строк в таблице.")
                        column = input("Введите номер или имя столбца: ")
                        table.set_values(values, column)
                        print("Значения установлены.")
                        try:
                            if selected_files[0][0].endswith(".csv"):
                                save_csv(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".pickle"):
                                save_pickle(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".txt"):
                                save_text(file_paths[0], table.headers, table.data)
                            print("Таблица сохранена.")
                        except Exception as e:
                            logger.error(f"Ошибка при сохранении файла: {e}")

                    elif operation == "8":
                        row_index = int(input("Введите номер строки: "))
                        column = input("Введите номер или имя столбца: ")
                        value = input("Введите новое значение: ")
                        table.set_value(row_index, column, value)
                        print("Значение установлено.")
                        try:
                            if selected_files[0][0].endswith(".csv"):
                                save_csv(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".pickle"):
                                save_pickle(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".txt"):
                                save_text(file_paths[0], table.headers, table.data)
                            print("Таблица сохранена.")
                        except Exception as e:
                            logger.error(f"Ошибка при сохранении файла: {e}")

                    elif operation == "9":
                        print("Загруженная таблица:")
                        table.print_table()
                        if len(file_paths) > 1:
                            combined_file_path = os.path.join(path, "TRANS.csv") if selected_files[0][0].endswith(".csv") else os.path.join(path, "TRANS.pickle")
                            if selected_files[0][0].endswith(".csv"):
                                save_combined_csv(combined_file_path, table.headers, table.data)
                            elif selected_files[0][0].endswith(".pickle"):
                                save_combined_pickle(combined_file_path, table.headers, table.data)

                    elif operation == "10":
                        row_number = int(input("Укажите номер строки, по которому хотите разделить таблицу: "))
                        top_half, bottom_half = table.split_table_by_row(row_number)
                        top_half_path = os.path.join(path, "top_half.csv") if selected_files[0][0].endswith(".csv") else os.path.join(path, "top_half.pickle")
                        bottom_half_path = os.path.join(path, "bottom_half.csv") if selected_files[0][0].endswith(".csv") else os.path.join(path, "bottom_half.pickle")
                        if selected_files[0][0].endswith(".csv"):
                            save_csv(top_half_path, top_half.headers, top_half.data)
                            save_csv(bottom_half_path, bottom_half.headers, bottom_half.data)
                        elif selected_files[0][0].endswith(".pickle"):
                            save_pickle(top_half_path, top_half.headers, top_half.data)
                            save_pickle(bottom_half_path, bottom_half.headers, bottom_half.data)
                        print("Таблица разделена и сохранена в файлах.")

                    elif operation == "11":
                        table.apply_operation()
                        print("Арифметическая операция применена.")
                        try:
                            if selected_files[0][0].endswith(".csv"):
                                save_csv(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".pickle"):
                                save_pickle(file_paths[0], table.headers, table.data)
                            elif selected_files[0][0].endswith(".txt"):
                                save_text(file_paths[0], table.headers, table.data)
                            print("Таблица сохранена.")
                        except Exception as e:
                            logger.error(f"Ошибка при сохранении файла: {e}")

                    elif operation == "12":
                        operation = input("Выберите операцию сравнения (==, >, <, >=, <=, !=): ").strip().lower()
                        if operation not in ["==", ">", "<", ">=", "<=", "!="]:
                            raise ValueError("Неверная операция сравнения")
                        bool_list = table.compare_columns(operation)
                        print("Результат сравнения:", bool_list)

                    elif operation == "13":
                        bool_list = eval(input("Введите список булевых значений (например, [True, False, True]): "))
                        if not isinstance(bool_list, list) or not all(isinstance(x, bool) for x in bool_list):
                            raise ValueError("Неверный формат списка булевых значений.")
                        copy_table = input("Копировать таблицу? (да/нет): ").lower() == "да"
                        result = table.filter_rows(bool_list, copy_table)
                        if copy_table:
                            print("Отфильтрованная таблица:")
                            result.print_table()
                        else:
                            print("Таблица отфильтрована.")

                    elif operation == "14":
                        return

                    else:
                        logger.error("Неверный выбор операции.")

                except ValueError as e:
                    logger.error(f"Ошибка: {e}")
                except Exception as e:
                    logger.error(f"Непредвиденная ошибка: {e}")

                choice = input("Вы хотите вернуться к выбору файла? (да/нет): ").strip().lower()
                if choice == 'да':
                    break
                elif choice == 'нет':
                    return

        elif action == "2":
            headers = ('ID ' + input("Введите заголовки через пробел: ")).split()
            if not headers:
                logger.error("Заголовки не могут быть пустыми.")
                continue
            try:
                row_count = int(input("Введите количество строк: "))
                if row_count <= 0:
                    raise ValueError("Количество строк должно быть положительным числом.")
                data = []
                for i in range(row_count):
                    row_input = input("Введите строку данных через пробел: ").split()
                    row = [str(i + 1)] + row_input
                    if len(row) < len(headers):
                        row.extend(['None'] * (len(headers) - len(row)))
                    data.append(row)

                try:
                    file_paths = [file_path for _, file_path in selected_files]
                    max_rows = int(input("Введите максимальное количество строк в файле: "))
                    if selected_files[0][0].endswith(".csv"):
                        save_csv(file_paths[0], headers, data, max_rows)
                    elif selected_files[0][0].endswith(".pickle"):
                        save_pickle(file_paths[0], headers, data, max_rows)
                    elif selected_files[0][0].endswith(".txt"):
                        save_text(file_paths[0], headers, data)
                    else:
                        logger.error("Неподдерживаемый формат файла для сохранения.")
                        continue
                    logger.info("Таблица сохранена.")
                except Exception as e:
                    logger.error(f"Ошибка при сохранении файла: {e}")

            except ValueError as e:
                logger.error(f"Ошибка: {e}")
            except Exception as e:
                logger.error(f"Непредвиденная ошибка: {e}")

        elif action == "3":
            try:
                file_paths = [file_path for _, file_path in selected_files]
                infer_types = input("Автоматически определить типы столбцов? (да/нет): ").strip().lower() == "да"
                if len(file_paths) > 1:
                    if selected_files[0][0].endswith(".csv"):
                        headers1, table_data1 = load_csv(file_paths[0], infer_types=infer_types)
                        headers2, table_data2 = load_csv(file_paths[1], infer_types=infer_types)
                    elif selected_files[0][0].endswith(".pickle"):
                        headers1, table_data1 = load_pickle(file_paths[0], infer_types=infer_types)
                        headers2, table_data2 = load_pickle(file_paths[1], infer_types=infer_types)
                    else:
                        logger.error("Неподдерживаемый формат файла для загрузки.")
                        continue
                else:
                    logger.error("Для объединения требуется два файла.")
                    continue

                table1 = Table(headers1, table_data1)
                table2 = Table(headers2, table_data2)

                by_number = input("Объединять по номеру строки? (да/нет): ").strip().lower() == "да"
                conflict_resolution = input("Способ разрешения конфликтов (first/second): ").strip().lower()

                merged_table = merge_tables(table1, table2, by_number=by_number, conflict_resolution=conflict_resolution)

                print("Объединенная таблица:")
                merged_table.print_table()

                combined_file_path = os.path.join(path, "MERGED.csv") if selected_files[0][0].endswith(".csv") else os.path.join(path, "MERGED.pickle")
                if selected_files[0][0].endswith(".csv"):
                    save_combined_csv(combined_file_path, merged_table.headers, merged_table.data)
                elif selected_files[0][0].endswith(".pickle"):
                    save_combined_pickle(combined_file_path, merged_table.headers, merged_table.data)

            except Exception as e:
                logger.error(f"Ошибка при объединении таблиц: {e}")

        else:
            logger.error("Неверный выбор действия.")
            continue

if __name__ == "__main__":
    main()
