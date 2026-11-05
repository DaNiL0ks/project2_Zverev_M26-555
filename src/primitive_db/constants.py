WELCOME_MESSAGE = "Первая попытка запустить проект!"
COMMAND_PROMPT = "Введите команду: "
HELP_TEXT = """
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> help - справочная информация
<command> exit - выход из программы
"""

META_FILE = "db_meta.json"
VALID_TYPES = ("int", "str", "bool")
DATA_DIR = "data"