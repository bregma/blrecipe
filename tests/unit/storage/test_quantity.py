"""
Test the Quantity storage model
"""
from unittest import TestCase
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
        query = session.query(Quantity).filter_by(string_id='GUI_MACHINE_CRAFT_TAB_SINGLE').first()
        self.assertTrue(query.string_id == 'GUI_MACHINE_CRAFT_TAB_SINGLE')
