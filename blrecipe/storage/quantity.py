"""
Quantity Classifications
"""

from sqlalchemy import Column, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from .database import BaseObject, Session


class Quantity(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of recipe quantities
    """

    __tablename__ = 'Quantity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    string_id = Column(String(8), ForeignKey('Translation.string_id'), nullable=False)
    display_name = relationship('Translation', foreign_keys=string_id)

    def __init__(self, string_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string_id = string_id

    def __repr__(self):
        return self.string_id


@event.listens_for(Quantity.__table__, 'after_create')
def _default_quantities(target, connection):
    session = Session(bind=connection)
    session.add(Quantity('GUI_MACHINE_CRAFT_TAB_SINGLE'))
    session.add(Quantity('GUI_MACHINE_CRAFT_TAB_BULK'))
    session.add(Quantity('GUI_MACHINE_CRAFT_TAB_MASS'))
    session.commit()
