from .FieldConstraint import FieldConstraint
from datetime import datetime


class DateTimeConstraint(FieldConstraint):
    def cast(self, bean, field, value):
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value

    def check(self, bean, field, value):
        return []
