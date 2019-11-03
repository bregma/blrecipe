"""
Archetypes loaded from attributes.msgpack
"""

from sqlalchemy import Column, Integer, Numeric, String
from .database import BaseObject


class AttrArchetype(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Attribute Archetypes as loaded from the attributes msgpack
    """

    __tablename__ = 'AttrArchetype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(32), nullable=False)
    name = Column(String(32), nullable=False)
    calculation = Column(String(32))
    category = Column(String(32))
    displayType = Column(String(32))
    displayName = Column(String(32))
    type = Column(String(32))
    min = Column(Numeric)
    max = Column(Numeric)
    isHinderance = Column(String(8))

    def __init__(self, target, name, *args, **kwargs):
        self.target = target
        self.name = name
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<AttrArchetype "{}"={}>'.format(self.name, self.value)


