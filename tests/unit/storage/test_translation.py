"""
Test the Translationmodel
"""
from unittest import TestCase
from blrecipe.storage import Translation


class TestTranslation(TestCase):
    """
    Validate the Translation table
    """

    def test_ctor(self):
        """
        Verify basic constructor
        """
        test_key = 'WOODCHUCK'
        test_value = 'Groundhog'

        translation = Translation(string_id=test_key, value=test_value)

        self.assertEqual(translation.string_id, test_key)
        self.assertEqual(translation.value, test_value)
        self.assertEqual(translation.lang, 'en')
