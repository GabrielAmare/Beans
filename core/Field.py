import re
from .Bean import Bean
from .FieldValues import FieldValues
from datetime import datetime, date
from .exceptions import *
from .field_constraints import *


class Field:
    _re_rpy = re.compile(r"^([!?*+])([a-zA-Z][a-zA-Z0-9_]*)\[([a-zA-Z][a-zA-Z0-9_]*)\]$")
    _re_var = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
    base_types = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'date': date,
        'datetime': datetime
    }
    _constraints_table = {
        'increment': IncrementConstraint,
        'regex': RegexConstraint,
        'range': RangeConstraint,
        'length': LengthConstraint,
        'default': DefaultValueConstraint
    }

    name: str
    type: str
    optional: bool
    multiple: bool

    @classmethod
    def _cast_rpy(cls, value):
        match = cls._re_rpy.match(value)
        if match:
            card_symbol, field_name, field_type = match.groups()
            optional, multiple = {
                '!': (False, False),
                '?': (True, False),
                '*': (True, True),
                '+': (False, True)
            }[card_symbol]
            return field_name, field_type, optional, multiple

    def __init__(self, **cfg):
        # DEFINING BASE INFORMATIONS
        if 'rpy' in cfg:
            rpy = cfg.pop('rpy')
            self.name, self.type, self.optional, self.multiple = self._cast_rpy(rpy)
        elif 'name' in cfg and 'type' in cfg:
            self.name = cfg.pop('name')
            self.type = cfg.pop('type')
            self.optional = cfg.pop('optional', False)
            self.multiple = cfg.pop('multiple', False)
        else:
            raise Exception(f"Field is missing information for 'name', 'type', 'optional' and/or 'multiple' ")

        assert self._re_var.match(self.name)
        assert self._re_var.match(self.type)
        assert isinstance(self.optional, bool)
        assert isinstance(self.multiple, bool)

        # DEFININING CONSTRAINTS
        self.constraints = []

        if self.type == 'date':
            self.constraints.append(DateConstraint())
        elif self.type == 'datetime':
            self.constraints.append(DateTimeConstraint())
        elif self.type not in Field.base_types:
            self.constraints.append(ForeignKeyConstraint())

        for key, cls in self._constraints_table.items():
            if key in cfg:
                val = cfg.pop(key)
                obj = cls._field_cast(val)
                if obj:
                    self.constraints.append(obj)

        if cfg:
            raise Exception(f"Field config has unparsed kwargs : " + ", ".join(cfg.keys()))

    def __call__(self, cls):
        cls.__add_field__(self)
        return cls

    def get_field_data_type(self):
        if not hasattr(self, '_type'):
            cls = Field.base_types.get(self.type)

            if cls is None:
                cls = Bean.get_class(self.type)

            if cls is None:
                raise Exception("Field Type not found {}".format(self.type))

            setattr(self, '_type', cls)

        return getattr(self, '_type')

    def cast_one(self, bean, value):
        for constraint in self.constraints:
            is_cast, value = constraint.cast(bean=bean, field=self, value=value)
            if is_cast:
                break

        return value

    def cast(self, bean, value):
        if self.multiple:
            if value is None:
                values = []
            elif hasattr(value, '__iter__'):
                values = [self.cast_one(bean, item) for item in value]
            else:
                values = [self.cast_one(bean, value)]

            return FieldValues(bean=bean, field=self, values=values)
        else:
            return self.cast_one(bean, value)

    def check_one(self, bean, value):
        if value is None and self.optional:
            return

        errors = []

        if not isinstance(value, self.get_field_data_type()):
            errors.append(InvalidDataTypeError(bean=bean, field=self, value=value))

        for constraint in self.constraints:
            errors.extend(constraint.check(bean=bean, field=self, value=value))

        return errors

    def check(self, bean, value):
        errors = []
        if self.multiple:
            assert isinstance(value, FieldValues)
            for item in value:
                item_errors = self.check_one(bean, item)
                errors.extend(item_errors)
        else:
            value_errors = self.check_one(bean, value)
            errors.extend(value_errors)

        assert None not in errors
        return errors

    def update(self, bean, value):
        """Method to replace the <bean> current value for <self> field by <value>"""
        if self.optional and value is None:
            if self.multiple:
                return FieldValues(bean=bean, field=self)
            else:
                return None
        else:
            value = self.cast(bean, value)
            errors = self.check(bean, value)
            if errors:
                raise JoinError(errors)
            else:
                return value

    def init(self, bean, value):
        """Method to setup the <bean> current value for <self> field as <value>"""
        if self.optional and value is None:
            if self.multiple:
                return FieldValues(bean=bean, field=self)
            else:
                return None
        else:
            value = self.cast(bean, value)
            errors = self.check(bean, value)
            if errors:
                raise Exception(errors)
            else:
                return value
