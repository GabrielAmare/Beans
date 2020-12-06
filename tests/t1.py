import unittest
from core import *


class Test1(unittest.TestCase):
    def test_standard_types(self):
        @Field(name="string", type="str")
        @Field(name="integer", type="int")
        @Field(name="decimal", type="float")
        @Field(name="boolean", type="bool")
        class C1(Bean):
            pass

        C1(string="xxx", integer=5, decimal=0.5, boolean=True)

    def test_date_type(self):
        from datetime import date

        @Field(name="date", type="date")
        class C2(Bean):
            pass

        C2(date=date.today())

    def test_datetime_type(self):
        from datetime import datetime

        @Field(name="datetime", type="datetime")
        class C3(Bean):
            pass

        C3(datetime=datetime.now())

    def test_multiple(self):
        @Field(name="values", type="int", multiple=True)
        class C4(Bean):
            pass

        v1 = C4()
        self.assertEqual(v1.values, FieldValues)
        self.assertEqual(len(v1.values), 0)

        v1.values.append(1)
        self.assertEqual(len(v1.values), 1)

        v1.values.extend([2, 3])
        self.assertEqual(len(v1.values), 3)

        v1.values.remove(2)
        self.assertEqual(len(v1.values), 2)


if __name__ == '__main__':
    unittest.main()
