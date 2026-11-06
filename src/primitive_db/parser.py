import shlex


def parse_value(raw_value):
    """Convert a command value into a string, integer, or boolean."""
    raw_value = raw_value.strip()
    if not raw_value:
        raise ValueError("Значение не может быть пустым.")
    if raw_value[0] in ('"', "'"):
        if len(raw_value) < 2 or raw_value[-1] != raw_value[0]:
            raise ValueError("Закрой кавычки вокруг значения.")
        parts = shlex.split(raw_value)
        if len(parts) != 1:
            raise ValueError("Ожидалось одно значение в кавычках.")
        return parts[0]
    lowercase_value = raw_value.lower()
    if lowercase_value == "true":
        return True
    if lowercase_value == "false":
        return False
    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(
            f"Некорректное значение: {raw_value}. Текст нужно брать в кавычки."
        ) from error


def parse_condition(raw_condition):
    """Parse a column and value pair into a dictionary."""
    column, separator, raw_value = raw_condition.partition("=")
    column = column.strip()
    if not separator:
        raise ValueError("Ожидалось условие в формате «столбец = значение».")
    if not column.isidentifier():
        raise ValueError(f'Некорректное имя столбца: "{column}".')
    return {column: parse_value(raw_value)}


def split_outside_quotes(text, separator=None):
    """Split text on a separator outside quoted strings."""
    parts = []
    start = 0
    quote = None
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if quote is not None:
            if char == "\\" and quote == '"':
                escaped = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == separator or (separator is None and char.isspace()):
            parts.append(text[start:index])
            start = index + 1
    if quote is not None:
        raise ValueError("Закрой кавычки вокруг значения.")
    parts.append(text[start:])
    return parts


def parse_values(raw_values):
    """Parse a parenthesized list of values for an INSERT command."""
    raw_values = raw_values.strip()
    if not (raw_values.startswith("(") and raw_values.endswith(")")):
        raise ValueError("Укажи значения в скобках, например («Анна», 22).")
    values_text = raw_values[1:-1]
    return [parse_value(part) for part in split_outside_quotes(values_text, ",")]


def parse_insert(command_text):
    """Return the table name and values from an INSERT command."""
    parts = command_text.split(maxsplit=4)
    if [word.lower() for word in parts[:2]] != ["insert", "into"]:
        raise ValueError("Команда добавления должна начинаться с INSERT INTO.")
    if len(parts) < 3:
        raise ValueError("После INSERT INTO укажи имя таблицы.")
    if len(parts) < 4 or parts[3].lower() != "values":
        raise ValueError("После имени таблицы ожидается ключевое слово VALUES.")
    if len(parts) < 5:
        raise ValueError(
            'После VALUES укажи значения в скобках. Пример: VALUES ("Анна", 22).'
        )
    return parts[2], parse_values(parts[4])


def parse_select(command_text):
    """Return the table name and optional condition from a SELECT command."""
    parts = command_text.split(maxsplit=4)
    if [word.lower() for word in parts[:2]] != ["select", "from"]:
        raise ValueError("Команда чтения должна начинаться с SELECT FROM.")
    if len(parts) < 3:
        raise ValueError("После SELECT FROM укажи имя таблицы.")
    table_name = parts[2]
    if len(parts) == 3:
        return table_name, None
    if parts[3].lower() != "where":
        raise ValueError("Для фильтрации после имени таблицы укажи WHERE.")
    if len(parts) < 5:
        raise ValueError("После WHERE укажи условие. Пример: WHERE age = 22.")
    return table_name, parse_where(parts[4])


def parse_delete(command_text):
    """Return the table name and required condition from a DELETE command."""
    parts = command_text.split(maxsplit=4)
    if [word.lower() for word in parts[:2]] != ["delete", "from"]:
        raise ValueError("Команда удаления должна начинаться с DELETE FROM.")
    if len(parts) < 3:
        raise ValueError("После DELETE FROM укажи имя таблицы.")
    if len(parts) < 4 or parts[3].lower() != "where":
        raise ValueError("Для удаления записей после имени таблицы укажи WHERE.")
    if len(parts) < 5:
        raise ValueError("После WHERE укажи условие. Пример: WHERE ID = 1.")
    return parts[2], parse_where(parts[4])


def parse_update(command_text):
    """Return the table name, assignments, and condition from an UPDATE."""
    parts = command_text.split(maxsplit=3)
    if not parts or parts[0].lower() != "update":
        raise ValueError("Команда обновления должна начинаться с UPDATE.")
    if len(parts) < 2:
        raise ValueError("После UPDATE укажи имя таблицы.")
    if len(parts) < 3 or parts[2].lower() != "set":
        raise ValueError("После имени таблицы ожидается ключевое слово SET.")
    if len(parts) < 4:
        raise ValueError("После SET укажи новое значение. Пример: SET age = 23.")
    words = [part for part in split_outside_quotes(parts[3]) if part]
    keywords = [word.lower() for word in words]
    try:
        where_index = keywords.index("where", 1)
    except ValueError as error:
        raise ValueError("Для обновления записей укажи условие WHERE.") from error
    set_text = " ".join(words[:where_index])
    where_text = " ".join(words[where_index + 1 :])
    if not where_text:
        raise ValueError("После WHERE укажи условие. Пример: WHERE ID = 1.")
    return parts[1], parse_condition(set_text), parse_where(where_text)


def parse_where(raw_where):
    """Parse one or more conditions joined by AND into a dictionary."""
    words = [part for part in split_outside_quotes(raw_where) if part]
    clauses = []
    current_clause = []
    for word in words:
        if word.lower() == "and" and current_clause:
            clauses.append(" ".join(current_clause))
            current_clause = []
        else:
            current_clause.append(word)
    clauses.append(" ".join(current_clause))
    conditions = {}
    for clause in clauses:
        parsed = parse_condition(clause)
        if conditions.keys() & parsed.keys():
            raise ValueError("В WHERE укажи каждый столбец только один раз.")
        conditions.update(parsed)
    return conditions