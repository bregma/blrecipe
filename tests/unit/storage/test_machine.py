"""
Test the Machine storage model
"""
from unittest import TestCase
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
        machine = session.query(Machine).filter_by(name='EXTRACTOR').first()
        self.assertTrue(machine.name == 'EXTRACTOR')
