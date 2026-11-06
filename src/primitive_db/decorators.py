import time


def handle_db_errors(func):
    """Display a readable message when a database command fails."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as error:
            print(f"Ошибка: не найден файл данных {error.filename or error}.")
        except KeyError as error:
            print(f"Ошибка: не найдена таблица или столбец {error}.")
        except ValueError as error:
            print(f"Ошибка: {error} Попробуйте снова.")
        except Exception as error:
            print(f"Непредвиденная ошибка: {error}")
        return None
    return wrapper


def confirm_action(action_name):
    """Ask for confirmation before running a destructive operation."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить «{action_name}»? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Print how long a successful function call took."""
    def wrapper(*args, **kwargs):
        started_at = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - started_at
        if result is not None:
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Create a function that caches successful results by key."""
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        if result is not None:
            cache[key] = result
        return result
    return cache_result