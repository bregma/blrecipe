"""
Recipe Ingredients

The recipe_quantity table relates Recipes and Ingredients by Quantity
"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from .database import BaseObject

RecipeIngredient = Table('RecipeIngredient', BaseObject.metadata,
                         Column('recipe_id', Integer, ForeignKey('Recipe.id')),
                         Column('item_id', Integer, ForeignKey('Item.id')),
                         Column('quantity_id', Integer, ForeignKey('Quantity.id')),
                         Column('amount', Integer, nullable=False, default=0))
