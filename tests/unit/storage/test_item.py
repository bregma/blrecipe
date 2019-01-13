"""
Test the Item storage model
"""
from unittest import TestCase
from blrecipe.storage import Item


class TestItem(TestCase):
    """
    Validate the Item table
    """

    def test_single(self):
        """
        Verify that a Spark Item exists in the table.
        """
        item = Item('HIPPOPOTAMUS', 'ITEM_TYPE_RIVER_HORSE')
        self.assertEqual(item.name, 'HIPPOPOTAMUS')
