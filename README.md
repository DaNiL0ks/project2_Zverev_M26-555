# Примитивная база данных

Консольная база данных на Python. Позволяет создавать таблицы, добавлять, искать, обновлять и удалять записи. 
Схемы таблиц и записи хранятся в JSON-файлах между запусками.

## Демонстрации

### Финальная — полный сценарий работы

[![Полная демонстрация базы данных](https://asciinema.org/a/xN09FsJqPwpRIknQ.svg)](https://asciinema.org/a/xN09FsJqPwpRIknQ)

### Этап 2 — управление таблицами

[![Управление таблицами](https://asciinema.org/a/mTNFmNEBD0wQ2cjP.svg)](https://asciinema.org/a/mTNFmNEBD0wQ2cjP)

### Этап 3 — CRUD-операции

[![CRUD-операции](https://asciinema.org/a/wTYSw1PUPFAC7JOc.svg)](https://asciinema.org/a/wTYSw1PUPFAC7JOc)

### Этап 4 — декораторы и кэширование

[![Декораторы и кэширование](https://asciinema.org/a/Ua8a9MVw8k8Arf9q.svg)](https://asciinema.org/a/Ua8a9MVw8k8Arf9q)

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
| `insert into <таблица> values (<значения>)` | Добавить запись. `ID` присваивается автоматически. |
| `select from <таблица>` | Показать все записи. |
| `select from <таблица> where <условие>` | Показать записи по условию. |
| `update <таблица> set <столбец> = <значение> where <условие>` | Обновить подходящие записи. |
| `delete from <таблица> where <условие>` | Удалить подходящие записи. |
| `info <таблица>` | Показать схему таблицы и количество записей. |

Строки указываются в кавычках, целые числа и булевы значения `true` и `false` — без кавычек. Несколько условий в `WHERE` можно соединить через `AND`.
Поддерживаемые типы столбцов: `int`, `str`, `bool`.
Столбец `ID:int` добавляется автоматически.

## Декораторы и кэширование

- Ошибки команд выводятся в терминал. После ошибки можно ввести следующую команду.
- `delete` и `drop_table` запрашивают подтверждение. Ответ `y` выполняет операцию, любой другой ответ отменяет её.
- `insert` и `select` показывают время выполнения.
- Повторный `select` с теми же условиями использует кэш. После изменения данных кэш этой таблицы сбрасывается.

### Пример работы

```text
create_table crud_demo name:str age:int is_active:bool
list_tables
insert into crud_demo values ("Анна Мария", 22, true)
insert into crud_demo values ("Иван", 25, false)
select from crud_demo
select from crud_demo where age = 22 AND is_active = true
update crud_demo set age = 23 where ID = 1
select from crud_demo where ID = 1
delete from crud_demo where ID = 2
y
info crud_demo
drop_table crud_demo
y
exit
```

