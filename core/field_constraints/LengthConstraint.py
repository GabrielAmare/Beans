from .FieldConstraint import FieldConstraint
from ..exceptions import ValueLengthError
from ..constants import NOT_NULL


class LengthConstraint(FieldConstraint):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    @classmethod
    def _field_cast(cls, value):
        if isinstance(value, tuple) and len(value) == 2:
            return cls(min_value=value[0], max_value=value[1])
        elif isinstance(value, int):
            return cls(min_value=value, max_value=value)
        elif value == NOT_NULL:
            return cls(min_value=1, max_value=float('inf'))
        elif value in (None, False):
            return None
        else:
            raise Exception

    def cast(self, bean, field, value):
        return False, value

    def check(self, bean, field, value):
        if not self.min_value <= len(value) <= self.max_value:
            return ValueLengthError(bean=bean, field=field, value=value)
