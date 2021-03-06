"""
Recipe Quantity

A recipe may have different requirements for differt target quantities
(single, bulk, mass).  This table provides those variations.
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class RecipeQuantity(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Qnatities in a recipe.
    """
    __tablename__ = 'ReciepQuantity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('Recipe.id'))
    quantity_id = Column(Integer, ForeignKey('Quantity.id'))
    spark = Column(Integer, nullable=False, default=0)
    wear = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=0)
    produces = Column(Integer, nullable=False, default=0)

    recipe = relationship('Recipe', back_populates='quantities')
    quantity = relationship('Quantity')

    def __init__(self, recipe, quantity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipe = recipe
        self.quantity = quantity

    @property
    def display_name(self):
        """Get the (localized) display name of the ingredient."""
        return self.quantity.name

    def __repr__(self):
        return ('<RecipeQuantity recipe:{} quantity:{}>'
                .format(self.recipe.item.name,
                        self.quantity.name))
