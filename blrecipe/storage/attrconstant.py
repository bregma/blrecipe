"""
Constants loaded from attributes.msgpack
"""

from sqlalchemy import Column, Integer, Numeric, String
from .database import BaseObject


class AttrConstant(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Attribute Constants as loaded from the attributes msgpack
    """

    __tablename__ = 'AttrConstant'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    value = Column(Numeric, nullable=False, default=0)

    def __init__(self, name, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.value = value

    def __repr__(self):
        return '<AttrConstant "{}"={}>'.format(self.name, self.value)


