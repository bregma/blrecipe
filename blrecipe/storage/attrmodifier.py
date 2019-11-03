"""
Modifiers loaded from attributes.msgpack
"""

from sqlalchemy import Column, Integer, Numeric, String
from .database import BaseObject


class AttrModifier(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Attribute Modifiers as loaded from the attributes msgpack
    """

    __tablename__ = 'AttrModifier'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    value = Column(Numeric, nullable=False, default=0)
    order = Column(Integer, nullable=False, default=0)
    type = Column(String(12), nullable=False, default="")

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def __repr__(self):
        return '<AttrModifier "{}"=({} {}>'.format(self.name, self.type, self.value)
