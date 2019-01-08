"""
Recipe Definitions
"""

from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from .database import BaseObject


class Recipe(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Recipes
    """

    __tablename__ = 'Recipe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(16), unique=True, nullable=False)
    machine_id = Column(Integer, ForeignKey('Machine.id'))
    xp = Column(Integer)
    heat = Column(Integer, nullable=False, default=0)
    handcraftable = Column(Boolean, nullable=False, default=False)
    power = Column(Integer, nullable=False, default=0)
    attribute = Column(String(32))
    attribute_level = Column(Integer)

    def __init__(self, json_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if json_data is not None:
            print('Recipe: json_data="{}"'.format(json_data))
            self.display_name = json_data['outputItem']

    def __repr__(self):
        return self.display_name
