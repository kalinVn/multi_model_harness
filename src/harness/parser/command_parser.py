from dataclasses import dataclass


COMMAND_PREFIX = "execute command"


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    arguments: list[str]


def parse_command(text: str) -> ParsedCommand | None:
    """Разборира входен текст до име на команда и нейните аргументи.

    Пример:
    Вход:  "execute command read_file test.txt"
    Изход: ParsedCommand(name="read_file", arguments=["test.txt"])
    """

    # Нормализираме входа чрез премахване на началните и крайните интервали. Например
    # " execute command read_file text.txt " става
    # "execute command read_file text.txt".

    normalized_command_text = text.strip()


    # Проверяваме дали нормализираният текст започва с COMMAND_PREFIX. Продължаваме
    # при "execute command read_file text.txt", но връщаме None при
    # "read_file text.txt".
    if not normalized_command_text.lower().startswith(COMMAND_PREFIX):
        return None

    # Премахваме COMMAND_PREFIX от началото и изчистваме интервалите. Например
    # "execute command read_file test.txt" става
    # "read_file test.txt".
    command_name = normalized_command_text[len(COMMAND_PREFIX):].strip()

    if not command_name:
        raise ValueError("Command name is missing.")

    parts = command_name.split()

    # Създаваме ParsedCommand, съдържащ името на командата и всички аргументи.
    # ParsedCommand само съхранява тези данни; не изпълнява командата.

    # Пример: "execute command write_file test1.txt test2.txt test3.txt"
    # създава name="write_file" и arguments=["test1.txt", "test2.txt",
    # "test3.txt"].
                                                                    
    return ParsedCommand(name=parts[0], arguments=parts[1:])
