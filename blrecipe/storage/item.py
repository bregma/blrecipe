"""
Items
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, object_session
from .database import BaseObject
from .recipe_ingredient import Ingredient
from .translation import Translation


class Item(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Items
    """

    __tablename__ = 'Item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    string_id = Column(String(64), ForeignKey('Translation.string_id'))
    build_xp = Column(Integer, nullable=False, default=0)
    mine_xp = Column(Integer, nullable=False, default=0)
    prestige = Column(Integer, nullable=False, default=0)
    coin_value = Column(Integer, nullable=False, default=0)
    list_type_id = Column(String(64), ForeignKey('Translation.string_id'))
    max_stack_size = Column(Integer, nullable=False, default=0)

    translation = relationship('Translation', foreign_keys=[string_id])
    list_type_tr = relationship('Translation', foreign_keys=[list_type_id])
    recipes = relationship('Recipe')

    def __init__(self, name, string_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.string_id = string_id
        self.coin_value = kwargs['coin_value']

    def __repr__(self):
        return '<Item {} ({})>'.format(self.name, self.display_name)

    @property
    def display_name(self):
        """
        Get the (localized) display name of the item.
        """
        return self.translation.value if self.translation else "unknown"

    @property
    def description_id(self):
        """
        Get the translation key for the item desciption.
        """
        return self.string_id + '_DESCRIPTION'

    @property
    def subtitle_id(self):
        """
        Get the translation key for the item subtitle.
        """
        return self.string_id + '_SUBTITLE'

    @property
    def description(self):
        """
        Get the (localized) description of the item.
        """
        result = object_session(self).query(Translation)\
                                     .filter_by(string_id=self.description_id)\
                                     .first()
        if result is not None:
            return result.value
        return ''

    @property
    def subtitle(self):
        """
        Get the (localized) subtitle of the item.
        """
        result = object_session(self).query(Translation)\
                                     .filter_by(string_id=self.subtitle_id)\
                                     .first()
        if result is not None:
            return result.value
        return ''

    @property
    def list_type(self):
        """
        Get the localized list type name (if any).
        """
        return self.list_type_tr.value if self.list_type_tr else None

    @property
    def uses(self):
        """
        Get the uses (noun, as in 'Used In') for the item.
        """
        result = object_session(self).query(Ingredient)\
                                     .filter_by(item_id=self.id)\
                                     .all()
        return sorted({use.recipe.item.display_name for use in result})


