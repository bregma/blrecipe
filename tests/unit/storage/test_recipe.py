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
        test_experience = 11

        recipe = Recipe(experience=test_experience)

        self.assertEqual(recipe.experience, test_experience)
        self.assertEqual(recipe.power, 0)
