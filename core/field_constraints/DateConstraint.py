from .FieldConstraint import FieldConstraint
from datetime import date


class DateConstraint(FieldConstraint):
    def cast(self, bean, field, value):
        if isinstance(value, date):
            return value
        elif isinstance(value, str):
            return date.fromisoformat(value)
        else:
            return value

    def check(self, bean, field, value):
        return []
