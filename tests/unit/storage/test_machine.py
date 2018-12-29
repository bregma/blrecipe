"""
Test the Machine storage model
"""
from unittest import TestCase
from sqlalchemy import exists
from blrecipe.storage import Database, Machine


class TestMachine(TestCase):
    """
    Validate the Machine table
    """

    def test_single(self):
        """
        Verify that a Workbench Machine exists in the table.
        """
        session = Database().session()
        self.assertTrue(session.query(exists().where(Machine.display_name == 'Workbench')).scalar())
