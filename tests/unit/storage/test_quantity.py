"""
Test the Quantity storage model
"""
from unittest import TestCase
from sqlalchemy import exists
from blrecipe.storage import Database, Quantity


class TestQuantity(TestCase):
    """
    Validate the Quantity table
    """

    def test_single(self):
        """
        Verify that the Single quantity exists in the table.
        """
        session = Database().session()
        self.assertTrue(session.query(exists().where(Quantity.display_name == 'Single')).scalar())
