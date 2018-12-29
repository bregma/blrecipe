"""
Test the Ingredient storage model
"""
from unittest import TestCase
from sqlalchemy import exists
from blrecipe.storage import Database, Ingredient


class TestIngredient(TestCase):
    """
    Validate the Ingredient table
    """

    def test_single(self):
        """
        Verify that a Spark Ingredient exists in the table.
        """
        session = Database().session()
        self.assertTrue(session.query(exists().where(Ingredient.display_name == 'Spark')).scalar())
