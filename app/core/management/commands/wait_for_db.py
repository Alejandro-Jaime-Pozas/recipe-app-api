# BECAUSE OF THE DIRECTORY STRUCTURE FOR THIS FILE ie: core > management > commands DJANGO WILL AUTO DETECT THIS FILE AS A MANAGEMENT COMMAND THAT IS ACCESSIBLE THROUGH python manage.py
"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# this is the minimum code required to run a django management command. use the BaseCommand class and the handle method to handle the command
class Command(BaseCommand):
    """Django command to wait for database."""

    # this handle method for BaseCommand is the method that is automatically run when running the command in CLI
    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...') # this stdout.write method writes a log to the command line
        db_up = False # set db is running to False
        while db_up is False:
            # try checking if there is a database ready, if not, handle the exception by waiting then running again
            try:
                self.check(databases=['default']) # checks if default database in django app
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1) # wait 1 second then run loop again to check for live database

        self.stdout.write(self.style.SUCCESS('Database available!!!'))
