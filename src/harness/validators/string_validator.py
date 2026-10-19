class StringValidator:
   
    @staticmethod
    def validate_string(value, path, nonempty=False):
        """
        Валидира, че подадената стойност е низ.

        Пример (валиден): "Здравей".
        Пример (невалиден): 123.
        Резултат: ValueError; nonempty=True отхвърля и празни низове или низове само с интервали.
        """
        if not isinstance(value, str) or (nonempty and not value.strip()):
            qualifier = "nonempty " if nonempty else ""
            raise ValueError(f"{path} must be a {qualifier}string")
        return value
