import prompt

from primitive_db.constants import COMMAND_PROMPT, HELP_TEXT, WELCOME_MESSAGE


def print_help():
    """Display the available commands."""
    print(HELP_TEXT)


def welcome():
    """Run the interactive loop for help and exit commands."""
    print(WELCOME_MESSAGE)
    print_help()
    while True:
        command = prompt.string(COMMAND_PROMPT).strip()
        if command == "help":
            print_help()
        elif command == "exit":
            break
        else:
            print(f"Функции {command} нет. Попробуйте снова.")



