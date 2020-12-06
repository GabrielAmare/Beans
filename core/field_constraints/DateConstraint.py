from .FieldConstraint import FieldConstraint
from datetime import date


class DateConstraint(FieldConstraint):
    def __repr__(self):
        return f"Should be a date object"

    def cast(self, bean, field, value):
        if isinstance(value, date):
            return True, value
        elif isinstance(value, str):
            return True, date.fromisoformat(value)
        else:
            return False, value

    def check(self, bean, field, value):
        return []
