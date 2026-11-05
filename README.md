# Примитивная база данных

Консольное приложение на Python для создания, просмотра и удаления таблиц.
Метаданные таблиц сохраняются в JSON-файле между запусками программы.

## Установка

Для работы необходимы Python 3.12, uv и Git.

```shell
git clone https://github.com/DaNiL0ks/project2_Zverev_M26-555.git
cd project2_Zverev_M26-555
uv sync
```

## Запуск

В корне проекта выполните:

```shell
uv run database
```

Также доступна команда `uv run project`.

## Управление таблицами

| Команда | Описание |
| --- | --- |
| `create_table <имя_таблицы> <столбец:тип> ...` | Создать таблицу |
| `list_tables` | Показать список таблиц |
| `drop_table <имя_таблицы>` | Удалить таблицу и её файл данных, если он существует |
| `help` | Показать справку |
| `exit` | Завершить работу |

Поддерживаемые типы столбцов: `int`, `str`, `bool`.
Столбец `ID:int` добавляется автоматически.

### Пример использования

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

Введите команду: list_tables
Список таблиц:
- users

Введите команду: drop_table users
Таблица "users" успешно удалена.

Введите команду: list_tables
Таблиц пока нет.

Введите команду: exit
```

## Демонстрация

[![Демонстрация управления таблицами](https://asciinema.org/a/mTNFmNEBD0wQ2cjP.svg)](https://asciinema.org/a/mTNFmNEBD0wQ2cjP)
