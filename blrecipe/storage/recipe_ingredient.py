"""
Recipe Ingredients

The recipe_quantity table relates Recipes and Ingredients by Quantity
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class Ingredient(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Ingredients in a recipe.
    """
    __tablename__ = 'Ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('Recipe.id'))
    item_id = Column(Integer, ForeignKey('Item.id'))
    quantity_id = Column(Integer, ForeignKey('Quantity.id'))
    amount = Column(Integer, nullable=False, default=0)

    recipe = relationship('Recipe', back_populates='ingredients')
    quantity = relationship('Quantity')
    item = relationship('Item')

    @property
    def display_name(self):
        """Get the (localized) display name of the ingredient."""
        return self.item.display_name

    def __repr__(self):
        return ('<Ingredient recipe:{} item:{} quantity:{} amount:{}>'
                .format(self.recipe.item.name,
                        self.quantity.display_name,
                        self.item.name,
                        self.amount))
