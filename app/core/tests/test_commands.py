from django.test import SimpleTestCase
from django.core.management import call_command
from unittest.mock import patch
from psycopg2 import OperationalError as PsyCopg2Error
from django.db.utils import OperationalError


@patch("core.management.commands.wait_for_db.Command.check")
class TestCommand(SimpleTestCase):

    def test_wait_for_db(self, patched_check):
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_with_delay(self, patched_sleep, patched_check):
        patched_check.side_effect = (
            [PsyCopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
