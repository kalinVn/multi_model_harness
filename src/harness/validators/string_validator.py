class StringValidator:
   
    @staticmethod
    def validate_string(value, path, nonempty=False):
        """
        Validate that the provided value is a string.

        Example (valid): "Hello".
        Example (invalid): 123.
        Result: ValueError; nonempty=True also rejects empty or whitespace-only strings.
        """
        if not isinstance(value, str) or (nonempty and not value.strip()):
            qualifier = "nonempty " if nonempty else ""
            raise ValueError(f"{path} must be a {qualifier}string")
        return value
