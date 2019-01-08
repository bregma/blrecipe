"""
Items
"""

from sqlalchemy import Column, Integer, String, event, DDL
from .database import BaseObject


class Item(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Items
    """

    __tablename__ = 'Item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    string_id = Column(String(32), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.string_id

event.listen(Item.__table__, 'after_create',  # pylint: disable=no-member
             DDL("""INSERT INTO Item (string_id)
                        VALUES ('Spark'),
                               ('Power'),
                               ('Wear'),
                               ('Time');"""))
