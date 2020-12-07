class FieldList(list):
    """
        Overriding the list class to allow the Bean functionalities
    """
    def __init__(self, bean, field, values=None):
        super().__init__()
        if values is None:
            values = []
        self.bean = bean
        self.field = field
        self.extend(values) if hasattr(values, '__iter__') else self.append(values)

    def append(self, value):
        value = self.field.cast_one(self.bean, value)
        self.field.check_one(self.bean, value)
        super().append(value)
        self.bean.callback(f"{self.field.name}:append", value)

    def remove(self, value):
        value = self.field.cast_one(self.bean, value)
        super().remove(value)
        self.bean.callback(f"{self.field.name}:remove", value)

    def extend(self, values):
        for value in values:
            self.append(value)
