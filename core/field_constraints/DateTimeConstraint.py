from .FieldConstraint import FieldConstraint
from datetime import datetime


class DateTimeConstraint(FieldConstraint):
    def __repr__(self):
        return f"Should be a datetime object"

    def cast(self, bean, field, value) -> tuple:
        if isinstance(value, datetime):
            return True, value
        elif isinstance(value, str):
            return True, datetime.fromisoformat(value)
        else:
            return False, value

    def check(self, bean, field, value):
        return []
