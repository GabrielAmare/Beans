from .constants import LAZY, EAGER, JSON, CREATE, UPDATE
from .RepositoryManager import RepositoryManager
from ..arrays import SymbolicArray
from datetime import datetime, date
from .functions import check_attribute


class Bean:
    uid: int

    @staticmethod
    def __get_classes__():
        for subcls in Bean._subclasses:
            yield subcls

    @staticmethod
    def __get_class__(name):
        for subclass in Bean.__get_classes__():
            if subclass.__name__ == name:
                return subclass

    """
        Bean :
            __debug_mode__ : If True, prevent field check errors to stop the runtime
            __file_mode__ : Mode used to save/load files in repository
                JSON : .json
                RAW : (no extensions)
            __repository__ : Repository manager object
                .root : Name of the main repository

            _subclasses : Bean subclasses list

        Bean subclasses :
            __repo_name__ : Name of the directory where Bean subclasses instances are stored (in the main repository)

            _fields : fields of the Bean subclass, used to cast/check the values
            _instances : instances of the Bean subclass, holds the runtime loaded instances
    """
    _fields = []
    _instances = []
    _subclasses = []

    __repository__: RepositoryManager = None
    __file_mode__: str = JSON
    __repo_name__: str = "bean"
    __debug_mode__: bool = False

    def __init_subclass__(cls, **kwargs):
        cls._fields = []
        cls._instances = []
        cls.__repo_name__ = kwargs.get('repo_name', cls.__name__.lower())
        Bean._subclasses.append(cls)

    def __setattr__(self, name, value, mode=UPDATE):
        field = self.__get_field__(name)
        if field:
            value = field.set(bean=self, value=value, mode=mode)
            super().__setattr__(field.name, value)
            self.callback(field.name, value)
            self.callback(field.name + ":" + mode, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return repr(self.to_dict())

    def __new__(cls, **config):
        instance = cls.get_by_id(config.get('uid'))

        if not instance:
            instance = super().__new__(cls)

        return instance

    def __init__(self, **config):
        if not hasattr(self, '_locked'):
            self._subscribes = {}
            self.onCreate(**config)
            self.__add_instance__(self)
            self._locked = True

    def apply_config(self, mode, **config):
        for name, value in config.items():
            self.__setattr__(name, value, mode)

    def onCreate(self, **config):
        """Function called when the instance is created"""
        # normalize config
        for field in self.__get_fields__():
            config.setdefault(field.name, None)
        self.apply_config(CREATE, **config)

    def onUpdate(self, **config):
        """Function called when the instance is updated"""
        self.apply_config(UPDATE, **config)

    def onDelete(self):
        """Function called when the instance is deleted"""
        pass

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

        if 'debug_mode' in config:
            Bean.__debug_mode__ = config.pop('debug_mode')

    @staticmethod
    def __init_repo__():
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        repo = Bean.__repository__
        repo.mkdir()

        for cls in Bean.__get_classes__():
            repo.mkdir(cls.__repo_name__)

    @classmethod
    def __get_instances__(cls) -> SymbolicArray:
        return SymbolicArray(cls._instances)

    @classmethod
    def __add_instance__(cls, instance):
        assert isinstance(instance, cls)
        cls._instances.append(instance)

    @classmethod
    def __del_instance__(cls, obj):
        instance = cls.__cast_instance__(obj)
        if instance in cls._instances:
            cls._instances.remove(instance)

    @classmethod
    def __cast_instance__(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, int):
            return cls.get_by_id(obj)
        else:
            raise Exception(f"Unable to cast {obj} into a {cls.__name__} instance")

    @classmethod
    def __get_fields__(cls):
        # TODO : implement overwrite of the fields with the same name
        fields = []
        for subclass in cls.__mro__:
            if issubclass(subclass, Bean):
                fields = subclass._fields + fields
        return fields

    @classmethod
    def __get_field__(cls, name):
        for field in cls.__get_fields__():
            if field.name == name:
                return field

    @classmethod
    def __add_field__(cls, field):
        cls._fields.insert(0, field)

    # TODO : implement __del_field__ (is it useful ?)

    @classmethod
    def get_by(cls, key, value):
        """Return the first instance found with the attr <key> is set to <value>"""
        assert cls.__get_field__(key), f"The field {cls.__name__}.{key} doesn't exist !"
        return cls.__get_instances__().keep(check_attribute(key, value)).first()

    @classmethod
    def get_by_id(cls, uid: int, load_if_not_found: bool = False, ignore_missing: bool = False):
        instance = cls.get_by('uid', uid)
        if isinstance(instance, cls):
            return instance
        elif Bean.__repository__ and load_if_not_found:
            return cls.load(uid, ignore_missing=ignore_missing)
        elif ignore_missing:
            return None
        else:
            raise Exception(f"{cls.__repo_name__}:{uid} has not been found !")

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

    @classmethod
    def load(cls, uid, ignore_missing=False):
        assert Bean.__repository__, f"Bean Repository is setup : Use Bean.__config__(repository='<your_repository>')"
        try:
            data = Bean.__repository__.read(
                path=cls.__repo_name__,
                name=uid,
                mode=cls.__file_mode__
            )
        except Exception as e:
            if ignore_missing:
                return
            else:
                raise e
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
            for b_cls in Bean.__get_classes__():
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
            for bean_cls in Bean.__get_classes__():
                bean_cls.__save_all__()
        else:
            for instance in cls.__get_instances__():
                instance.save()

    @classmethod
    def __delete_all__(cls):
        if cls is Bean:
            for b_cls in Bean.__get_classes__():
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
