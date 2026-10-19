def read_input() -> str:
    """Read one message from the terminal."""

    try:
        user_input = input("You > ")
    except (EOFError, KeyboardInterrupt):
        return "exit"

    return user_input.strip()