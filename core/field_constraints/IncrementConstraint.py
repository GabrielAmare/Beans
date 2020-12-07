from .FieldConstraint import FieldConstraint
from ..constants import UNIT


class IncrementConstraint(FieldConstraint):
    def __init__(self, start, step):
        self.start = start
        self.step = step

    @classmethod
    def _field_cast(cls, value):
        if isinstance(value, tuple) and len(value) == 2:
            return cls(start=value[0], step=value[1])
        elif value == UNIT:
            return cls(start=0, step=1)
        elif value in (None, False):
            return None
        else:
            raise Exception

    def cast(self, bean, field, value):
        # TODO : set a way to recalculate the max-value each time it's need for the next one
        #  it will help when looking for calculation optimizations
        #  something like bean.max_field_value(field) -> current_max (max_field_value is a classmethod)
        value = bean.__class__\
                    .__get_instances__()\
                    .getattr(field.name)\
                    .max(default=self.start) + self.step
        return True, value

    def check(self, bean, field, value):
        return []
