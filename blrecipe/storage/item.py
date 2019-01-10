"""
Items
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class Item(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Items
    """

    __tablename__ = 'Item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    string_id = Column(String(64), ForeignKey('Translation.string_id'))
    display_name = relationship('Translation')

    def __init__(self, name, string_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.string_id = string_id

    def __repr__(self):
        return '<Item {}>'.format(self.name)