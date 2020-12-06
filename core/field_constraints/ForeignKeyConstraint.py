from ..Bean import Bean
from .FieldConstraint import FieldConstraint
from ..exceptions import InvalidDataTypeError


class ForeignKeyConstraint(FieldConstraint):
    def cast(self, bean, field, value) -> tuple:
        bean_cls = field.get_field_data_type()
        if isinstance(value, bean_cls):
            return True, value
        elif isinstance(value, int):
            instance = bean_cls.get_by_id(value)
            if isinstance(instance, bean_cls):
                return True, instance
            elif Bean.__repository__:
                try:
                    return True, bean_cls.load(value)
                except Exception as e:
                    pass
        return False, value

    def check(self, bean, field, value):
        if not issubclass(value.__class__, Bean):
            return [InvalidDataTypeError(bean=bean, field=field, constraint=self, value=value)]
        else:
            return []
