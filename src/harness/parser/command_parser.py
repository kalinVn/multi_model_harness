from dataclasses import dataclass


COMMAND_PREFIX = "execute command"


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    arguments: list[str]


def parse_command(text: str) -> ParsedCommand | None:
    """Парсва входния текст и връща ParsedCommand с името
    на командата и нейните аргументи.

    Пример:
    Вход:  "execute command read_file test.txt"
    Изход: ParsedCommand(name="read_file", arguments=["test.txt"])
    """

    #  # Нормализира входния текст, като премахва празните символи в началото и края. Пример: Вход: "execute command read_file text.txt"
    # резултат: "execute command read_file text.txt", без начални и крайни интервали.

    normalized_command_text = text.strip()


    # проверява дали нормализираният текст започва с COMMAND_PREFIX — например, "execute command".
    # Пример: ако входът е "execute command read_file text.txt", продължаваме напред.
    # Ако входът е "read_file text.txt", връщаме None.
    if not normalized_command_text.lower().startswith(COMMAND_PREFIX):
        return None

     # премахва COMMAND_PREFIX от началото на текста... и изчиства празните символи.
    # " Пример: "execute command read_file test.txt", става "read_file test.txt
    command_name = normalized_command_text[len(COMMAND_PREFIX):].strip()

    if not command_name:
        raise ValueError("Command name is missing.")

    parts = command_name.split()

    # Създава обект ParsedCommand, който съдържа име на командата и списък с аргументи.
    # Ако има повече аргументи, те всички влизат в списъка arguments.
    # Важно: ParsedCommand само съхранява тези данни, не изпълнява командата.

    # Пример: вход "execute command write_file test1.txt test2 test3.txt", след сплит получаваш
    # write_file test1 test2 test3.
    # ParsedCommand ще създаде обект с name="write_file" и arguments=[ "test1.txt", "test2.txt", "test3.txt"]
                                                                    
    return ParsedCommand(
        name=parts[0],
        arguments=parts[1:],
    )
