from primitive_db.constants import PYTHON_TYPES, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a table schema with an automatic integer ID column."""
    if not table_name.isidentifier():
        raise ValueError(f'Некорректное имя таблицы: "{table_name}".')
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    checked_columns = {}
    for column in columns:
        if column.count(":") != 1:
            raise ValueError(f"Некорректное описание столбца: {column}.")
        column_name, column_type = column.split(":")
        if not column_name.isidentifier():
            raise ValueError(f'Некорректное имя столбца: "{column_name}".')
        if column_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректный тип '{column_type}' "
                f"для столбца '{column_name}'."
            )
        if column_name in checked_columns:
            raise ValueError(
                f"Дублирующееся имя столбца '{column_name}' "
                f"в таблице '{table_name}'."
            )
        if column_name == 'ID' and column_type != 'int':
            raise ValueError("Столбец 'ID' должен быть типа 'int'.")
        checked_columns[column_name] = column_type
    final_columns = {"ID": "int"}
    final_columns.update(checked_columns)

    metadata[table_name] = final_columns
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Remove an existing table schema from metadata."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Add a validated record with an automatic ID and return the table records."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    table_schema = metadata[table_name]
    if len(values) != len(table_schema) - 1:
        raise ValueError(
            f"Количество значений ({len(values)}) "
            f"не соответствует количеству столбцов ({len(table_schema) - 1})."
        )
    record = dict(zip(list(table_schema)[1:], values))
    if validate_column_values(table_schema, record) is None:
        return None
    table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Return table records that match the given conditions."""
    if where_clause is None:
        return table_data
    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        if match:
            filtered_data.append(record)
    return filtered_data


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Update matching records and return the full table data."""
    if not where_clause:
        raise ValueError("Условие WHERE не может быть пустым для обновления.")
    matching_records = select(table_data, where_clause)
    if matching_records is None:
        return None
    for record in matching_records:
        for column in set_clause:
            if column not in record:
                raise ValueError(f"Столбец '{column}' не существует в таблице.")
    for record in matching_records:
        record.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Return the table records after removing rows that match the conditions."""
    if not where_clause:
        raise ValueError("Условие WHERE не может быть пустым для удаления.")
    matching_records = select(table_data, where_clause)
    if matching_records is None:
        return None
    ids_to_delete = {record["ID"] for record in matching_records}
    return [record for record in table_data if record["ID"] not in ids_to_delete]


@handle_db_errors
def validate_column_values(table_schema, values):
    """Check that each column exists and its value has the declared type."""
    for column_name, value in values.items():
        if column_name not in table_schema:
            raise ValueError(f"Столбец '{column_name}' не существует в таблице.")
        column_type = table_schema[column_name]
        if type(value) is not PYTHON_TYPES[column_type]:
            raise ValueError(
                f"Неверный тип для столбца '{column_name}': "
                f"ожидался {column_type}, получен {type(value).__name__}."
            )
    return True