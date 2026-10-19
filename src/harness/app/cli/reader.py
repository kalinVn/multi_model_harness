def read_input() -> str:
    """Прочита едно съобщение от терминала."""

    try:
        user_input = input("You > ")
    except (EOFError, KeyboardInterrupt):
        return "exit"

    return user_input.strip()