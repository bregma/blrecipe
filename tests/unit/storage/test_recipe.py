"""
Test the Recipe storage model
"""
from unittest import TestCase
from blrecipe.storage import Recipe


class TestRecipe(TestCase):
    """
    Validate the Recipe model.
    """

    def test_ctor(self):
        """
        Validate the basic class constructor.
        """
        test_display_name = "test"

        recipe = Recipe(display_name=test_display_name)

        self.assertEqual(recipe.display_name, test_display_name)
