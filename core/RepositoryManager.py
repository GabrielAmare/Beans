import os
import json
from .constants import JSON, RAW


class RepositoryManager:
    default_mode = RAW

    def __init__(self, root):
        self.root = root

    def mkdir(self, path=''):
        real = os.path.join(self.root, path)
        if not os.path.exists(real):
            os.mkdir(real)

    def listdir(self, path=''):
        real = os.path.join(self.root, path)
        return os.listdir(real)

    def _get_path(self, path, name, mode=default_mode):
        if mode == JSON:
            return os.path.join(self.root, path, f"{name}.json")
        elif mode == RAW:
            return os.path.join(self.root, path, f"{name}")
        else:
            raise Exception(f"Unknown file mode")

    def exists(self, path, name, mode=default_mode):
        if mode == JSON:
            real = self._get_path(path, name, mode)
            return os.path.exists(real)
        else:
            raise Exception(f"Unknown file mode")

    def create(self, path, name, data, mode=default_mode):
        if mode == JSON:
            real = self._get_path(path, name, mode)
            assert not os.path.exists(real)
            file = open(real, encoding="utf-8", mode="w")
            json.dump(data, file)
        else:
            raise Exception(f"Unknown file mode")

    def read(self, path, name, mode=default_mode):
        if mode == JSON:
            real = self._get_path(path, name, mode)
            assert os.path.exists(real)
            file = open(real, encoding="utf-8", mode="r")
            data = json.load(file)
            return data
        else:
            raise Exception(f"Unknown file mode")

    def read_all(self, path, mode=default_mode):
        if mode == JSON:
            for filename in self.listdir(path):
                if filename.endswith('.json'):
                    real = os.path.join(self.root, path, filename)
                    file = open(real, encoding="utf-8", mode="r")
                    data = json.load(file)
                    yield data
        else:
            raise Exception(f"Unknown file mode")

    def update(self, path, name, data, mode=default_mode, ignore_missing=False):
        if mode == JSON:
            real = self._get_path(path, name, mode)
            if os.path.exists(real):
                if not ignore_missing:
                    raise Exception(
                        f"File {real} does not and can't be updated (set 'ignore_missing' to True to force creation) !")
            file = open(real, encoding="utf-8", mode="w")
            json.dump(data, file)
        else:
            raise Exception(f"Unknown file mode")

    def delete(self, path, name, mode=default_mode, ignore_missing=False):
        if mode == JSON:
            real = self._get_path(path, name, mode)
            if os.path.exists(real):
                os.remove(real)
            elif not ignore_missing:
                raise Exception(f"File {real} does not exist and can't be deleted !")
        else:
            raise Exception(f"Unknown file mode")

    def delete_all(self, path, mode=default_mode):
        if mode == JSON:
            for filename in self.listdir(path):
                if filename.endswith('.json'):
                    real = os.path.join(self.root, path, filename)
                    os.remove(real)
        else:
            raise Exception(f"Unknown file mode")
