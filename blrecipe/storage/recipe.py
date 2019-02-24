"""
Recipe Definitions
"""

from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class Recipe(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Recipes
    """

    __tablename__ = 'Recipe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('Item.id'), nullable=False)
    machine_id = Column(Integer, ForeignKey('Machine.id'))
    experience = Column(Integer, nullable=False, default=0)
    heat = Column(Integer, nullable=False, default=0)
    handcraftable = Column(Boolean, nullable=False, default=False)
    power = Column(Integer, nullable=False, default=0)
    attribute = Column(String(32))
    attribute_level = Column(Integer)

    item = relationship('Item')
    machine = relationship('Machine')
    ingredients = relationship('Ingredient', back_populates='recipe')
    quantities = relationship('RecipeQuantity', back_populates='recipe')

    def __init__(self,
                 experience=None,
                 heat=None,
                 handcraftable=None,
                 power=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.experience = experience if experience else 0
        self.heat = heat if heat else 0
        self.power = power if power else 0
        self.handcraftable = handcraftable if handcraftable else 0

    def __repr__(self):
        return '<Recipe "{}">'.format(self.item.display_name)
