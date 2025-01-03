'''
Sample tests
'''
# SimpleTestCase does NOT require a temp db created by django for testing, so tests run faster
# TestCase does include temp db creation for each individual test, use wisely
from django.test import SimpleTestCase # can also import TestCase for more complex tests

from . import calc

class CalcTests(SimpleTestCase):
    '''Test the calc module.'''

    # methods from django tests should always start with 'test' keyword for them to be picked up by django, non 'test' named fns can be used for reference
    def test_add_numbers(self):
        '''Test adding numbers together.'''
        res = calc.add(5,6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        '''Test subtracting numbers'''
        res = calc.subtract(10, 15)

        self.assertEqual(res, 5)

    def test_divide(self):
        '''Subtracts 2nd number from 1st number.'''
        res = calc.divide(12, 3)

        self.assertEqual(res, 4)
