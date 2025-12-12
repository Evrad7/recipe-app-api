from django.core.management.base import BaseCommand
import time
from django.db.utils import OperationalError
from psycopg2 import OperationalError as PsyCopg2Error


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Checking for availability of db ...")

        while True:
            try:
                self.check(databases=["default"])
                self.stdout.write("Database is available !!!")
                break
            except (OperationalError, PsyCopg2Error):
                self.stdout.write(
                    "Database is not available yet, waiting 1s to retry"
                )
                time.sleep(1)
