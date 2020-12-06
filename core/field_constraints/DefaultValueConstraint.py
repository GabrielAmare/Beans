from .FieldConstraint import FieldConstraint


class DefaultValueConstraint(FieldConstraint):
    def __init__(self, default, is_function):
        self.default = default
        self.is_function = is_function

    @classmethod
    def _field_cast(cls, value):
        if isinstance(value, tuple) and len(value) == 2:
            return cls(default=value[0], is_function=value[1])
        elif hasattr(value, '__call__'):
            return cls(default=value, is_function=True)
        elif value is None:
            return None
        else:
            return cls(default=value, is_function=False)

    def cast(self, bean, field, value):
        if value is None:
            if self.is_function:
                return True, self.default()
            else:
                return True, self.default
        else:
            return False, value

    def check(self, bean, field, value):
        return []
