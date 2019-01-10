"""
Test the Item storage model
"""
from unittest import TestCase
from sqlalchemy import exists
from blrecipe.storage import Database, Item


class TestItem(TestCase):
    """
    Validate the Item table
    """

    def test_single(self):
        """
        Verify that a Spark Item exists in the table.
        """
        session = Database().session()
        print('==smw !!! <==wms')
        self.assertTrue(session.query(exists().where(Item.string_id == 'Spark')).scalar())
