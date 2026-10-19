import json


class CommandResponseValidator:
    """Валидира структурирания отговор, върнат за команда."""

    def validate(self, response_text: str) -> bool:
        """
        Валидира, че JSON на командата има поле answer от тип низ и непразно поле summary.

        Пример (валиден): '{"answer": "Готово", "command_summary": "Файлът е актуализиран"}'.
        Пример (невалиден): '{"answer": "Готово", "command_summary": ""}'.
        Резултат: False при невалидни данни; този метод не генерира грешки при валидация.
        """
        try:
            payload = json.loads(response_text)
        except (json.JSONDecodeError, TypeError):
            return False

        if not isinstance(payload, dict):
            return False

        answer = payload.get("answer")
        command_summary = payload.get("command_summary")

        if not isinstance(answer, str):
            return False

        if not isinstance(command_summary, str) or not command_summary.strip():
            return False

        return True
