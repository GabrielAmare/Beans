from .FieldConstraint import FieldConstraint
from ..exceptions import InvalidRegexMatchError
import re


class RegexConstraint(FieldConstraint):
    def __init__(self, pattern, flags):
        self.regex = re.compile(pattern=pattern, flags=flags)

    @classmethod
    def _field_cast(cls, value):
        if isinstance(value, tuple) and len(value) == 2:
            return cls(pattern=value[0], flags=value[1])
        elif isinstance(value, str):
            return cls(pattern=value, flags=0)
        elif value in (None, False):
            return None
        else:
            raise Exception

    def cast(self, bean, field, value):
        return False, value

    def check(self, bean, field, value):
        if not self.regex.match(value):
            yield InvalidRegexMatchError(bean=bean, field=self, value=value)
