class FieldValues(list):
    def __init__(self, bean, field, values):
        super().__init__()
        self.bean = bean
        self.field = field
        self.extend(values) if hasattr(values, '__iter__') else self.append(value)

    def append(self, value):
        value = self.field.unit_cast(self.bean, value)
        self.field.unit_check(self.bean, value)
        super().append(value)

    def extend(self, values):
        for value in values:
            self.append(value)