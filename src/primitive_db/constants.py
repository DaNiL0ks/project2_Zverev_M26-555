WELCOME_MESSAGE = "Первая попытка запустить проект!"
COMMAND_PROMPT = "Введите команду: "
HELP_TEXT = (
    "\n***База данных***\n"
    "Функции:\n"
    "<command> create_table <имя_таблицы> <столбец:тип> ... - создать таблицу\n"
    "<command> list_tables - показать список всех таблиц\n"
    "<command> drop_table <имя_таблицы> - удалить таблицу\n"
    "<command> insert into <имя_таблицы> values (<значения>) - добавить запись\n"
    "<command> select from <имя_таблицы> [where <условие>] - прочитать записи\n"
    "<command> update <имя_таблицы> set <столбец> = <значение> "
    "where <условие> - обновить записи\n"
    "<command> delete from <имя_таблицы> where <условие> - удалить записи\n"
    "<command> info <имя_таблицы> - показать информацию о таблице\n"
    "\nОбщие команды:\n"
    "<command> help - справочная информация\n"
    "<command> exit - выход из программы\n"
)

META_FILE = "db_meta.json"
PYTHON_TYPES = {"int": int, "str": str, "bool": bool}
VALID_TYPES = tuple(PYTHON_TYPES)
DATA_DIR = "data"