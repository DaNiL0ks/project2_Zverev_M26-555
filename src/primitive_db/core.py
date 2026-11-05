from primitive_db.constants import VALID_TYPES


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


def drop_table(metadata, table_name):
    """Remove an existing table schema from metadata."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    return metadata