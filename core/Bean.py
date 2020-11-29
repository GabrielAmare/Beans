import sys
import json
import os
from .constants import LAZY, EAGER
from .FieldValues import FieldValues
from datetime import datetime, date


class Bean:
    _debug = True

    _fields = []
    _instances = []
    _subclasses = []

    _repository = None

    def __init_subclass__(cls, **kwargs):
        cls._fields = []
        cls._instances = []
        Bean._subclasses.append(cls)

    def __setattr__(self, name, value):
        field = self.__get_field__(name)
        if field:
            value = field.cast(self, value)
            error = field.check(self, value)
            if error:
                if Bean._debug:
                    print(error, file=sys.stderr)
                else:
                    raise error
            if hasattr(self, name):
                old = getattr(self, name)
            else:
                old = None

        if field and field.multiple:
            if not hasattr(self, name):
                if hasattr(value, '__iter__'):
                    super().__setattr__(name, FieldValues(bean=self, field=field, values=value))
                elif value is None:
                    super().__setattr__(name, FieldValues(bean=self, field=field, values=[]))
                else:
                    super().__setattr__(name, FieldValues(bean=self, field=field, values=[value]))
            else:
                field_values = getattr(self, name)
                if isinstance(field_values, FieldValues):
                    if hasattr(value, '__iter__'):
                        field_values.extend(value)
                    else:
                        field_values.append(value)
                else:
                    raise Exception(f"FieldValues expected for a Field with 'multiple' option")

        else:
            super().__setattr__(name, value)

        if field:
            self.callback(field.name, old, value)

    def __new__(cls, **config):
        uid = config.get('uid')

        instance = cls.get_by_id(uid)

        if not instance:
            instance = super().__new__(cls)
            instance.__init__(**config)

        return instance

    def __init__(self, **config):
        if not hasattr(self, '_locked'):
            self._subscribes = {}

            for field in self.__get_fields__():
                value = config.get(field.name, None)
                self.__setattr__(field.name, value)
            self.__add_instance__(self)
            self._locked = True

    @classmethod
    def __add_instance__(cls, instance):
        assert isinstance(instance, cls)
        cls._instances.append(instance)

    @classmethod
    def __get_instances__(cls):
        for instance in cls._instances:
            yield instance

    @classmethod
    def __add_field__(cls, field):
        cls._fields.insert(0, field)

    @classmethod
    def __get_fields__(cls):
        fields = []
        for s_cls in cls.__mro__:
            if issubclass(s_cls, Bean):
                fields = s_cls._fields + fields
        return fields

    @classmethod
    def __get_field__(cls, name):
        for field in cls.__get_fields__():
            if field.name == name:
                return field

    @classmethod
    def get_by_id(cls, uid):
        for instance in cls._instances:
            if instance.uid == uid:
                return instance

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self, mode=EAGER) -> dict:
        def cast(value):
            if isinstance(value, Bean):
                if mode == LAZY:
                    return value.uid
                elif mode == EAGER:
                    return value.to_dict()
                else:
                    raise Exception(f"Wrong mode for Bean.to_dict method")
            elif isinstance(value, datetime):
                return value.isocalendar()
            elif isinstance(value, date):
                return value.isoformat()
            else:
                return value

        data = {}
        for field in self.__get_fields__():
            value = getattr(self, field.name)
            if issubclass(field.data_type, (Bean, datetime, date)):
                if field.multiple:
                    if hasattr(value, '__iter__'):
                        value = list(map(cast, value))
                else:
                    value = cast(value)

            if not ((value is None or isinstance(value, list) and len(value) == 0) and mode == LAZY):
                data[field.name] = value
        return data

    @classmethod
    def from_json(cls, fp: str):
        file = open(fp, encoding="utf-8", mode="r")
        data = json.load(file)
        bean = cls.from_dict(data)
        return bean

    def to_json(self, fp: str, mode=LAZY):
        file = open(fp, encoding="utf-8", mode="w")
        data = self.to_dict(mode=mode)
        json.dump(data, file)

    @classmethod
    def load(cls, uid):
        fp = os.path.join(cls.get_repository(), str(uid))
        bean = cls.from_json(fp)
        return bean

    def save(self, mode=LAZY):
        assert Bean._repository is not None
        assert os.path.exists(Bean._repository)

        fp = os.path.join(self.get_repository(), str(self.uid))
        return self.to_json(fp, mode=mode)

    @classmethod
    def load_all(cls):
        if cls is Bean:
            for b_cls in Bean._subclasses:
                b_cls.load_all()
        else:
            fp = cls.get_repository()
            for uid in os.listdir(fp):
                cls.load(uid)

    @classmethod
    def save_all(cls):
        if cls is Bean:
            for bean_cls in Bean._subclasses:
                bean_cls.save_all()
        else:
            for instance in cls.__get_instances__():
                instance.save()

    @staticmethod
    def __config__(**config):
        if 'repository' in config:
            Bean._repository = config.pop('repository')

            if not os.path.exists(Bean._repository):
                os.mkdir(Bean._repository)

    @classmethod
    def get_repository(cls):
        if cls is Bean:
            return Bean._repository
        else:
            return os.path.join(Bean._repository, cls.__name__.lower())

    @classmethod
    def init_repository(cls):
        if cls is Bean:
            assert Bean._repository is not None

            dir_path = Bean.get_repository()
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            for b_cls in Bean._subclasses:
                b_cls.init_repository()
        else:
            for b_cls in Bean._subclasses:
                dir_path = b_cls.get_repository()
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

    @classmethod
    def delete_all(cls):
        if cls is Bean:
            for b_cls in Bean._subclasses:
                b_cls.delete_all()
        else:
            dir_path = cls.get_repository()
            for uid in os.listdir(dir_path):
                file_path = os.path.join(dir_path, uid)
                os.remove(file_path)

    def match_config(self, **config):
        """Return True if self matches the configuration"""
        return all(getattr(self, key) == val for key, val in config.items())

    @classmethod
    def get_by_config(cls, **config):
        """For a given configuration, seek for the first instance that correspond and returns it"""
        for instance in cls._instances:
            if instance.match_config(**config):
                return instance

    def subscribe(self, name, function):
        self._subscribes.setdefault(name, [])
        self._subscribes[name].append(function)
        return lambda: self._subscribes[name].remove(function)

    def callback(self, key, *args, **kwargs):
        for function in self._subscribes.get(key, []):
            function(*args, **kwargs)

    @staticmethod
    def get_class(name):
        for subclass in Bean._subclasses:
            if subclass.__name__ == name:
                return subclass
