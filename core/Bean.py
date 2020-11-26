import sys
import json
import os
from .constants import LAZY, EAGER


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

        super().__setattr__(name, value)

    def __new__(cls, **config):
        uid = config.get('uid')

        instance = cls.get_by_id(uid)

        if not instance:
            instance = super().__new__(cls)
            instance.__init__(**config)

        return instance

    def __init__(self, **config):
        if not hasattr(self, '_locked'):
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
        data = {}
        for field in self.__get_fields__():
            value = getattr(self, field.name)
            if isinstance(value, Bean):
                if mode == LAZY:
                    value = value.uid
                elif mode == EAGER:
                    value = value.to_dict()
                else:
                    raise Exception(f"Wrong mode for Bean.to_dict method")

            if not (value is None and mode == LAZY):
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
