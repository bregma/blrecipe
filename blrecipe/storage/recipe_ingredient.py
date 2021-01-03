"""
Recipe Ingredients

The recipe_quantity table relates Recipes and Ingredients by Quantity
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class Ingredient(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Ingredients in a recipe.

    An ingredient has a group or an item but not both.
    """
    __tablename__ = 'Ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('Recipe.id'))
    item_id = Column(Integer, ForeignKey('Item.id'))
    group_name = Column(Integer, ForeignKey('IngredientGroup.name'))
    quantity_id = Column(Integer, ForeignKey('Quantity.id'))
    amount = Column(Integer, nullable=False, default=0)

    recipe = relationship('Recipe', back_populates='ingredients')
    quantity = relationship('Quantity')
    item = relationship('Item')

    @property
    def display_name(self):
        """Get the (localized) display name of the ingredient."""
        return self.group_name if self.group_name else self.item.name()

    def __repr__(self):
        return ('<Ingredient recipe:{} item:{} quantity:{} amount:{}>'
                .format(self.recipe.item.name(),
                        self.quantity.display_name,
                        self.item.name(),
                        self.amount))


class IngredientGroup(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Ingredient groups for a recipe.

    This table is stored in denormalized form.
    """
    __tablename__ = 'IngredientGroup'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    item_id = Column(Integer, ForeignKey('Item.id'))

    item = relationship('Item')

    def __init__(self, name, item_id):
        self.name = name
        self.item_id = item_id


