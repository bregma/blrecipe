"""
Ingredients
"""

from sqlalchemy import Column, Integer, String, event, DDL
from .database import BaseObject


class Ingredient(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Ingredients
    """

    __tablename__ = 'Ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(32), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.display_name


event.listen(Ingredient.__table__, 'after_create',  # pylint: disable=no-member
             DDL("""INSERT INTO Ingredient (display_name)
                        VALUES ('Spark'),
                               ('Power'),
                               ('Wear'),
                               ('Time');"""))
