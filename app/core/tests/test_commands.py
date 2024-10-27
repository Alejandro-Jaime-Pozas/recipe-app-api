"""
Test custom Django mgmt commands.
"""
from unittest.mock import patch # needed to MOCK the behavior of the database, to save time testing vs actually depending on database behavior

from psycopg2 import OperationalError as Psycopg2Error # one possible error we may receive before the database is ready

from django.core.management import call_command # helper fn that allows us to call the command that we're testing
from django.db.utils import OperationalError # another exception we might encounter when database is created/run
from django.test import SimpleTestCase # basic testing for unit tests. using simple test to avoid migrations folder etc needed for a standard database


# @patch() decorator to mock functions. we're going to simulate database running without actually running it
# path in @patch() is the path to the Command class in this core directory. the 'check' is a method built into the BaseCommand class that our Command class is inheriting from. check allows us to check the status of the database.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    # one possible test case is that we run the wait for command and db is already ready
    def test_wait_for_db_ready(self, patched_check):  # patched_check obj return from @patch decorator and we'll use it to customize the behavior
        """Test waiting for database if database ready."""
        patched_check.return_value = True  # .return_value to indicate a value

        call_command('wait_for_db')  # will execute the code inside our 'wait_for_db' file

        patched_check.assert_called_once_with(databases=['default'])  # this ensures that the mocked obj which is returned by the 'check' method is called with the database parameter


    # another test case is that we run the wait for command and db is not ready, and we want to wait a few seconds and try again
    # in terms of argument calls in class methods like test_wait_for_db_delay, the order of ops is the most inner @patch() decorator is called first, then the next outer one, which is why patched_sleep is included BEFORE the patched_check obj
    @patch('time.sleep') # mock the sleep method
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when waiting for OperationalError."""
        # side_effect allows you to handle various items depending on their type. if we pass in a boolean, it will return the boolean value, if we pass in an exception then the mocking library knows that is should raise that exception.
        # side_effects are called in the ORDER they are called. first 2 times: Psycopg2 error, next 3 times: OperationalError, next time: True
        # this was all done by instructor w/trial and error
        # the values: * 2, * 3 are just arbitrary numbers that are realistic to what would happen when testing the database readiness
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + \
            [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6) # checking that the 'check' command in @patch decorator fn is being called exactly 6 times as input in side_effect
        patched_check.assert_called_with(databases=['default']) # using called_with vs called_once_with since there's multiple calls being made here
