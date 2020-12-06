class JoinError(Exception):
    """Used to join multiple errors into one"""

    def __init__(self, errors):
        self.errors = errors

    def __repr__(self):
        return "\n".join(map(repr, self.errors))


class FieldValueError(Exception):
    message: str
    header: str = "{bean.__class__.__name__}.{field.name}: "

    def __init__(self, bean, field, value):
        self.bean = bean
        self.field = field
        self.value = value

    def __repr__(self):
        return (self.header + self.message).format(**self.__dict__)


class InvalidDataTypeError(FieldValueError):
    """Raised when the value doesn't correspond to the expected type of the field"""
    message = "{field.type} != {value.__class__.__name__}"


class InvalidRegexMatchError(FieldValueError):
    """Raised when the value doesn't correspond to the specified regex of the field"""
    message = "{value} should match r{field.regex.__repr__()}"


class ValueNotInRangeError(FieldValueError):
    """Raised when the value is not in the specified range of the field"""
    message = "{value} should be in range [{field.min_value}: {field.max_value}]"


class ValueLengthError(FieldValueError):
    """Raised when the value length is not in the specified range of the field"""
    message = "{value} length should be in range [{field.min_value}: {field.max_value}]"
