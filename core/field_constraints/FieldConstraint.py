class FieldConstraint:
    priority = 0

    @classmethod
    def _field_cast(cls, value):
        pass

    def cast(self, bean, field, value) -> tuple:
        """
            Return : has_been_casted, casted_value
            if it hasn't been casted, means that the next caster should take it
        """
        return False, value

    def check(self, bean, field, value) -> list:
        """
            Return the list of errors when cheking the value (empty list means no errors)
        :param bean:
        :param field:
        :param value:
        :return:
        """
        return []
