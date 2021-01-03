"""
Items
"""

from sqlalchemy import Column, Integer, String, ForeignKey, or_
from sqlalchemy.orm import relationship, object_session
from .database import BaseObject
from .recipe_ingredient import Ingredient, IngredientGroup
from .translation import ItemName, Translation


class Item(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Items
    """

    __tablename__ = 'Item'
    id = Column(Integer, primary_key=True)
    string_id = Column(String(64))
    build_xp = Column(Integer, nullable=False, default=0)
    mine_xp = Column(Integer, nullable=False, default=0)
    prestige = Column(Integer, nullable=False, default=0)
    coin_value = Column(Integer, nullable=False, default=0)
    list_type_id = Column(String(64), ForeignKey('Translation.string_id'))
    max_stack_size = Column(Integer, nullable=False, default=0)

    list_type_tr = relationship('Translation', foreign_keys=[list_type_id])
    recipes = relationship('Recipe')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Item {} ({})>'.format(self.id, self.name(language='english'))

    def name(self, language='english'):
        """
        Get the (localized) display name of the item.
        """
        result = object_session(self).query(ItemName)\
                                     .filter_by(item_id=self.id,
                                                lang=language)\
                                     .first()
        if result is not None:
            return result.name
        return '[[unknown]]'

    @property
    def description_id(self):
        """
        Get the translation key for the item desciption.
        """
        return self.string_id + '_DESCRIPTION'

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

    def subtitle(self, language='english'):
        """
        Get the (localized) subtitle of the item.
        """
        result = object_session(self).query(ItemName)\
                                     .filter_by(item_id=self.id,
                                                lang=language)\
                                     .first()
        if result is not None:
            return result.subtitle
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

        An item may be an explicit ingredient in a recipe or as an alternative
        in a group ingredient.

        There is probably a better way to do this using a single query with a
        join but this works for now.
        """
        group_rows = object_session(self).query(IngredientGroup)\
                                         .filter_by(item_id=self.id)\
                                         .all()
        if len(group_rows) > 0:
            group_names = [group.name for group in group_rows]
            result = object_session(self).query(Ingredient)\
                                         .filter(or_(Ingredient.item_id==self.id,
                                                     Ingredient.group_name.in_(group_names)))\
                                         .all()
        else:
            result = object_session(self).query(Ingredient)\
                                         .filter(Ingredient.item_id==self.id)\
                                         .all()
        return sorted({use.recipe.item.name() for use in result})


