import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import COMMAND_PROMPT, HELP_TEXT, META_FILE, WELCOME_MESSAGE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
    validate_column_values,
)
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import parse_delete, parse_insert, parse_select, parse_update
from primitive_db.utils import (
    delete_table_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

select_cachers = {}


def print_help():
    """Display the available commands."""
    print(HELP_TEXT)


@handle_db_errors
def handle_insert(metadata, command_text):
    """Insert a record, save the table, and report the assigned ID."""
    table_name, values = parse_insert(command_text)
    table_data = insert(metadata, table_name, values)
    if table_data is None:
        return
    save_table_data(table_name, table_data)
    select_cachers.pop(table_name, None)
    new_id = table_data[-1]["ID"]
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


@handle_db_errors
def handle_select(metadata, command_text):
    """Select matching records and display them as a table."""
    table_name, where_clause = parse_select(command_text)
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    table_schema = metadata[table_name]
    if where_clause is not None:
        if validate_column_values(table_schema, where_clause) is None:
            return
    if table_name not in select_cachers:
        select_cachers[table_name] = create_cacher()
    cache_result = select_cachers[table_name]
    conditions_key = tuple(sorted((where_clause or {}).items()))
    matching_records = cache_result(
        conditions_key,
        lambda: select(load_table_data(table_name), where_clause),
    )
    if matching_records is None:
        return
    columns = list(table_schema)
    result_table = PrettyTable(columns)
    for record in matching_records:
        result_table.add_row([record[column] for column in columns])
    print(result_table)


@handle_db_errors
def handle_update(metadata, command_text):
    """Update matching records, save the table, and report their IDs."""
    table_name, set_clause, where_clause = parse_update(command_text)
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    table_schema = metadata[table_name]
    if "ID" in set_clause:
        raise ValueError("Столбец ID нельзя изменять.")
    if validate_column_values(table_schema, set_clause) is None:
        return
    if validate_column_values(table_schema, where_clause) is None:
        return
    table_data = load_table_data(table_name)
    matching_records = select(table_data, where_clause)
    if matching_records is None:
        return
    if not matching_records:
        print("Подходящих записей не найдено.")
        return
    updated_data = update(table_data, set_clause, where_clause)
    if updated_data is None:
        return
    save_table_data(table_name, updated_data)
    select_cachers.pop(table_name, None)
    for record in matching_records:
        record_id = record["ID"]
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


@handle_db_errors
def handle_delete(metadata, command_text):
    """Delete matching records, save the table, and report their IDs."""
    table_name, where_clause = parse_delete(command_text)
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    if validate_column_values(metadata[table_name], where_clause) is None:
        return
    table_data = load_table_data(table_name)
    matching_records = select(table_data, where_clause)
    if matching_records is None:
        return
    if not matching_records:
        print("Подходящих записей не найдено.")
        return
    remaining_records = delete(table_data, where_clause)
    if remaining_records is None:
        return
    save_table_data(table_name, remaining_records)
    select_cachers.pop(table_name, None)
    for record in matching_records:
        record_id = record["ID"]
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def format_columns(table_schema):
    """Format schema columns as comma-separated name:type pairs."""
    return ", ".join(
        f"{column}:{column_type}" for column, column_type in table_schema.items()
    )


@handle_db_errors
def handle_info(metadata, args):
    """Display a table's schema and record count."""
    if len(args) != 2:
        raise ValueError("Укажи одно имя таблицы. Пример: info users.")
    table_name = args[1]
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    columns_text = format_columns(metadata[table_name])
    record_count = len(load_table_data(table_name))
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {record_count}")


@handle_db_errors
def handle_create_table(metadata, args):
    """Create a table, save its schema, and report the result."""
    if len(args) < 3:
        raise ValueError("Укажи имя и столбцы. Пример: create_table users name:str.")
    table_name = args[1]
    columns = args[2:]
    updated_metadata = create_table(metadata, table_name, columns)
    if updated_metadata is None:
        return
    save_metadata(META_FILE, updated_metadata)
    columns_text = format_columns(updated_metadata[table_name])
    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_text}"
    )
    return updated_metadata


@handle_db_errors
def handle_drop_table(metadata, args):
    """Drop a table and clear its cached queries after confirmation."""
    if len(args) != 2:
        raise ValueError("Укажи одно имя таблицы. Пример: drop_table users.")
    table_name = args[1]
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    updated_metadata = drop_table(metadata, table_name)
    if updated_metadata is None:
        return None
    delete_table_file(table_name)
    save_metadata(META_FILE, updated_metadata)
    select_cachers.pop(table_name, None)
    print(f'Таблица "{table_name}" успешно удалена.')
    return updated_metadata


def run():
    """Run the database command loop and dispatch user commands."""
    print(WELCOME_MESSAGE)
    print_help()
    while True:
        try:
            metadata = load_metadata(META_FILE)
        except (OSError, ValueError) as error:
            print(f'Не удалось загрузить метаданные из "{META_FILE}": {error}')
            return
        user_input = prompt.string(COMMAND_PROMPT).strip()
        try:
            args = shlex.split(user_input)
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
            continue
        if not args:
            continue
        command = args[0]
        if command == "help":
            print_help()
        elif command == "exit":
            break
        elif command == "list_tables":
            if not metadata:
                print("Таблиц пока нет.")
            else:
                print("Список таблиц:")
                for table_name in metadata:
                    print(f"- {table_name}")
        elif command == "create_table":
            updated_metadata = handle_create_table(metadata, args)
            if updated_metadata is not None:
                metadata = updated_metadata
        elif command == "drop_table":
            updated_metadata = handle_drop_table(metadata, args)
            if updated_metadata is not None:
                metadata = updated_metadata
        elif command == "insert":
            handle_insert(metadata, user_input)
        elif command == "select":
            handle_select(metadata, user_input)
        elif command == "update":
            handle_update(metadata, user_input)
        elif command == "delete":
            handle_delete(metadata, user_input)
        elif command == "info":
            handle_info(metadata, args)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
