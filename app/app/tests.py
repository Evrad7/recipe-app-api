from app.calc import add, substract
from django.test import SimpleTestCase


class TestCalc(SimpleTestCase):

    def test_add(self):
        self.assertEqual(add(1, 2), 3)

    def test_substract(self):
        res = substract(7, 2)
        self.assertEqual(res, 5)
