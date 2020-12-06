import sys
from .constants import LAZY, EAGER, JSON
from .FieldValues import FieldValues
from .RepositoryManager import RepositoryManager
from datetime import datetime, date


class Bean:
    _debug = True

    _fields = []
    _instances = []
    _subclasses = []

    __repository__: RepositoryManager = None
    __file_mode__: str = JSON
    __repo_name__: str = "bean"

    def __init_subclass__(cls, **kwargs):
        cls._fields = []
        cls._instances = []
        cls.__repo_name__ = cls.__name__.lower()
        Bean._subclasses.append(cls)

    def __setattr__(self, name, value):
        field = self.__get_field__(name)
        if field:
            if hasattr(self, name):
                value = field.update(self, value)
            else:
                value = field.init(self, value)

        super().__setattr__(name, value)

        if field:
            self.callback(field.name, value)

        if field:
            value = field.cast(self, value)
            errors = field.check(self, value)
            if errors:
                if Bean._debug:
                    for error in errors:
                        print(error, file=sys.stderr)
                else:
                    raise Exception(errors)
            if hasattr(self, name):
                old = getattr(self, name)
            else:
                old = None

        if field and field.multiple:
            if not hasattr(self, name):
                super().__setattr__(name, value)
                # if hasattr(value, '__iter__'):
                #     super().__setattr__(name, FieldValues(bean=self, field=field, values=value))
                # elif value is None:
                #     super().__setattr__(name, FieldValues(bean=self, field=field, values=[]))
                # else:
                #     super().__setattr__(name, FieldValues(bean=self, field=field, values=[value]))
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

    def __repr__(self):
        return repr(self.to_dict())

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
                super().__setattr__(field.name, field.init(self, value))
            self.__add_instance__(self)
            self._locked = True

    @staticmethod
    def __setup__(create_db=True, reset_db=False, load_db=True):
        if create_db:
            Bean.__init_repo__()

        if reset_db:
            Bean.__delete_all__()

        if load_db:
            Bean.__load_all__()

    @staticmethod
    def __config__(**config):
        if 'repository' in config:
            repository = config.pop('repository')
            if Bean.__repository__:
                Bean.__repository__.root = repository
            else:
                Bean.__repository__ = RepositoryManager(root=repository)

        if 'file_mode' in config:
            Bean.__file_mode__ = config.pop('file_mode')

    @staticmethod
    def __get_subclasses__():
        for subcls in Bean._subclasses:
            yield subcls

    @staticmethod
    def __init_repo__():
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        repo = Bean.__repository__
        repo.mkdir()

        for cls in Bean.__get_subclasses__():
            repo.mkdir(cls.__repo_name__)

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
    def get_by(cls, key, value):
        """Return the first instance found with the attr <key> is set to <value>"""
        assert cls.__get_field__(key), f"The field {cls.__name__}.{key} doesn't exist !"
        for instance in cls._instances:
            if getattr(instance, key) == value:
                return instance

    @classmethod
    def get_by_id(cls, uid: int, load_if_not_found: bool = False):
        instance = cls.get_by('uid', uid)
        if isinstance(instance, cls):
            return instance
        elif Bean.__repository__ and load_if_not_found:
            try:
                return cls.load(uid)
            except:
                return None

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
                return value.isoformat()
            elif isinstance(value, date):
                return value.isoformat()
            else:
                return value

        data = {}
        for field in self.__get_fields__():
            value = getattr(self, field.name)
            if issubclass(field.get_field_data_type(), (Bean, datetime, date)):
                if field.multiple:
                    if hasattr(value, '__iter__'):
                        value = list(map(cast, value))
                else:
                    value = cast(value)

            if not ((value is None or isinstance(value, list) and len(value) == 0) and mode == LAZY):
                data[field.name] = value
        return data

    # @classmethod
    # def from_json(cls, fp: str):
    #     file = open(fp, encoding="utf-8", mode="r")
    #     data = json.load(file)
    #     bean = cls.from_dict(data)
    #     return bean
    #
    # def to_json(self, fp: str, mode=LAZY):
    #     file = open(fp, encoding="utf-8", mode="w")
    #     data = self.to_dict(mode=mode)
    #     json.dump(data, file)

    @classmethod
    def load(cls, uid):
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        data = Bean.__repository__.read(
            path=cls.__repo_name__,
            name=uid,
            mode=cls.__file_mode__
        )
        bean = cls.from_dict(data)
        return bean

    def save(self, mode=LAZY):
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        Bean.__repository__.update(
            path=self.__repo_name__,
            name=self.uid,
            data=self.to_dict(mode=mode),
            mode=self.__file_mode__,
            ignore_missing=True
        )

    def delete(self):
        """Delete the corresponding file and the instance"""
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        print(f'deleting {self.__repo_name__}.{self.uid}')
        Bean.__repository__.delete(
            path=self.__repo_name__,
            name=self.uid,
            mode=self.__file_mode__,
            ignore_missing=True
        )

    @classmethod
    def __load_all__(cls):
        if cls is Bean:
            for b_cls in Bean.__get_subclasses__():
                b_cls.__load_all__()
        else:
            for data in Bean.__repository__.read_all(
                    path=cls.__repo_name__,
                    mode=cls.__file_mode__
            ):
                cls.from_dict(data)

    @classmethod
    def __save_all__(cls):
        if cls is Bean:
            for bean_cls in Bean.__get_subclasses__():
                bean_cls.__save_all__()
        else:
            for instance in cls.__get_instances__():
                instance.save()

    @classmethod
    def __delete_all__(cls):
        if cls is Bean:
            for b_cls in Bean.__get_subclasses__():
                b_cls.__delete_all__()
        else:
            # delete the loaded instances
            while cls._instances:
                instance = cls._instances.pop(0)
                instance.delete()
                del instance

            # delete the remaining files
            cls.__repository__.delete_all(
                path=cls.__repo_name__,
                mode=cls.__file_mode__
            )

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
