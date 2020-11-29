import re
from .Bean import Bean


class Field:
    invalid_data_type = "Invalid data type for '{cls_name}.{field_name}' : Should be '{expected_type}' instead of '{actual_type}'"
    invalid_regex_match = "Value doesn't match regex in '{cls_name}.{field_name}' : '{actual_value}' should match '{expected_regex}'"

    def __init__(self, name: str, type: str, increment=None, optional=False, multiple=False, regex=None,
                 default_value=None, default_value_function=None):
        assert re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name)
        self.name = name
        # assert type in ('str', 'int', 'float', 'list', 'dict')
        self.type = type
        self.increment = increment
        self.optional = optional
        self.multiple = multiple
        self.default_value = default_value
        self.default_value_function = default_value_function
        self.regex = regex

        assert not (self.default_value and self.default_value_function)

        assert not (self.optional and self.increment), "Optional and Increment options are incompatible"
        assert not self.regex or self.type == "str"

        self._data_type = None

    def __call__(self, cls):
        cls.__add_field__(self)
        return cls

    @property
    def data_type(self):
        if self._data_type is None:
            if self._data_type is None:
                for bean_cls in Bean._subclasses:
                    if bean_cls.__name__ == self.type:
                        self._data_type = bean_cls
                        break
                else:
                    self._data_type = eval(self.type)
        return self._data_type

    def unit_cast(self, bean, value):
        if self.increment and value is None:
            start, step = self.increment
            values = [getattr(instance, self.name) for instance in bean.__class__.__get_instances__()]
            return max(values, default=start) + step

        if isinstance(value, int) and issubclass(self.data_type, Bean):
            for instance in self.data_type.__get_instances__():
                if instance.uid == value:
                    return instance

            if Bean._repository:
                return self.data_type.load(value)

        if value is None:
            if self.default_value is not None:
                return self.default_value
            elif self.default_value_function is not None:
                return self.default_value_function()

        return value

    def cast(self, bean, value):
        if self.multiple:
            if hasattr(value, '__iter__'):
                value = [self.unit_cast(bean, item) for item in value]
            else:
                value = [self.unit_cast(bean, value)]
            value = [item for item in value if item is not None]
            if not len(value):
                value = None
            return value
        else:
            return self.unit_cast(bean, value)

    def unit_check(self, bean, value):
        if value is None and self.optional:
            return

        if not isinstance(value, self.data_type):
            return Exception(self.invalid_data_type.format(
                cls_name=bean.__class__.__name__,
                field_name=self.name,
                expected_type=self.type,
                actual_type=value.__class__.__name__
            ))

        if self.regex and not re.match(self.regex, value):
            return Exception(self.invalid_regex_match.format(
                cls_name=bean.__class__.__name__,
                field_name=self.name,
                expected_regex=self.regex,
                actual_value=value
            ))

    def check(self, bean, value):
        if self.multiple:
            if hasattr(value, '__iter__'):
                errors = [self.unit_check(bean, item) for item in value]
            else:
                errors = [self.unit_check(bean, value)]
            errors = [error for error in errors if error is not None]
            return errors
        else:
            return self.unit_check(bean, value)
