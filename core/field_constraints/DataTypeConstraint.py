import re
from .FieldConstraint import FieldConstraint
from ..exceptions import InvalidDataTypeError


class DataTypeConstraint(FieldConstraint):
    regex_int = re.compile('^[0-9]+$')
    regex_float = re.compile('^\-?([0-9]+.[0-9]*|[0-9]*.[0-9]+|inf)$')
    regex_bool = re.compile('True|False')

    def cast(self, bean, field, value) -> tuple:
        datatype = field.get_field_data_type()
        if isinstance(value, datatype):
            return True, value
        elif isinstance(value, str) and datatype is int and self.regex_int.match(value):
            return True, int(value)
        elif isinstance(value, str) and datatype is float and self.regex_float.match(value):
            return True, float(value)
        elif isinstance(value, str) and datatype is bool and self.regex_bool.match(value):
            return True, float(value)
        else:
            return False, value

    def check(self, bean, field, value):
        if not isinstance(value, field.get_field_data_type()):
            return [InvalidDataTypeError(bean=bean, field=field, constraint=self, value=value)]
        else:
            return []
