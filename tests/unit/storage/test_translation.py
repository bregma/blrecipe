"""
Test the Translation module
"""
from unittest import TestCase
from blrecipe.storage import Translation, ItemName


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
        test_language = 'english'

        translation = Translation(string_id=test_key, value=test_value)

        self.assertEqual(translation.string_id, test_key)
        self.assertEqual(translation.value, test_value)
        self.assertEqual(translation.lang, test_language)


class TestItemName(TestCase):
    """
    Validate the ItemNamen table
    """

    def test_ctor(self):
        """
        Verify basic constructor
        """
        test_item_id = 1024
        test_language='inuktitut'
        test_name = 'Groundhog'

        item_name = ItemName(item_id=test_item_id, lang=test_language, name=test_name)

        self.assertEqual(item_name.item_id, test_item_id)
        self.assertEqual(item_name.name, test_name)
        self.assertEqual(item_name.lang, test_language)
