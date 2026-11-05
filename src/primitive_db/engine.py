import shlex

import prompt

from primitive_db.constants import COMMAND_PROMPT, HELP_TEXT, META_FILE, WELCOME_MESSAGE
from primitive_db.core import create_table, drop_table
from primitive_db.utils import delete_table_file, load_metadata, save_metadata


def print_help():
    """Display the available commands."""
    print(HELP_TEXT)


def run():
    """Run the database command loop and dispatch user commands."""
    print(WELCOME_MESSAGE)
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
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
            if len(args) < 3:
                print(
                    "Недостаточно аргументов для команды create_table.\n"
                    "Формат: create_table <имя_таблицы> <столбец:тип> ...\n"
                    "Пример: create_table users name:str age:int"
                )
                continue
            table_name = args[1]
            columns = args[2:]
            try:
                metadata = create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)
                columns_text = ", ".join(
                    f"{column_name}:{column_type}"
                    for column_name, column_type in metadata[table_name].items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {columns_text}"
                )
            except ValueError as error:
                print(f"Ошибка: {error} Попробуйте снова.")
        elif command == "drop_table":
            if len(args) != 2:
                print(
                    "Укажите одно имя таблицы для удаления.\n"
                    "Формат: drop_table <имя_таблицы>\n"
                    "Пример: drop_table users"
                )
                continue
            table_name = args[1]
            try:
                metadata = drop_table(metadata, table_name)
                delete_table_file(table_name)
                save_metadata(META_FILE, metadata)
                print(f'Таблица "{table_name}" успешно удалена.')
            except ValueError as error:
                print(f"Ошибка: {error} Попробуйте снова.")
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
