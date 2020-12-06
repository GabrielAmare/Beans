from .FieldConstraint import FieldConstraint
from ..exceptions import ValueNotInRangeError
from ..constants import POSITIVE, NEGATIVE, UNIT, PERCENT


class RangeConstraint(FieldConstraint):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    @classmethod
    def _field_cast(cls, value):
        if isinstance(value, tuple) and len(value) == 2:
            return cls(min_value=value[0], max_value=value[1])
        elif value == POSITIVE:
            return cls(min_value=0, max_value=float('inf'))
        elif value == NEGATIVE:
            return cls(min_value=-float('inf'), max_value=0)
        elif value == UNIT:
            return cls(min_value=0, max_value=1)
        elif value == PERCENT:
            return cls(min_value=0, max_value=100)
        elif value in (None, False):
            return None
        else:
            raise Exception

    def cast(self, bean, field, value):
        return False, value

    def check(self, bean, field, value):
        if not self.min_value <= value <= self.max_value:
            return ValueNotInRangeError(bean=bean, field=field, value=value)
