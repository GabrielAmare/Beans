class JoinError(Exception):
    """Used to join multiple errors into one"""

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "Error log :\n" + "\n".join(f"    {error}" for error in self.errors)


class FieldValueError(Exception):
    message: str
    header: str = "{bean.__class__.__name__}.{field.name}: "

    def __init__(self, bean, field, constraint, value):
        self.bean = bean
        self.field = field
        self.constraint = constraint
        self.value = value

    def __str__(self):
        return (self.header + self.message).format(**self.__dict__)


class InvalidDataTypeError(FieldValueError):
    """Raised when the value doesn't correspond to the expected type of the field"""
    message = "{field.type} != {value.__class__.__name__}"


class InvalidRegexMatchError(FieldValueError):
    """Raised when the value doesn't correspond to the specified regex of the field"""
    message = "{value!r} should match r{constraint.regex.__repr__()}"


class ValueNotInRangeError(FieldValueError):
    """Raised when the value is not in the specified range of the field"""
    message = "{value!r} should be in range [{constraint.min_value}: {constraint.max_value}]"


class ValueLengthError(FieldValueError):
    """Raised when the value length is not in the specified range of the field"""
    message = "{value!r} length should be in range [{constraint.min_value}: {constraint.max_value}]"
