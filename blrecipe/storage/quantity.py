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
    quantity_id = Column('id', Integer, primary_key=True)
    string_id = Column(String(64), ForeignKey('Translation.string_id'))
    display_name = relationship('Translation')

    def __init__(self, quantity_id, string_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quantity_id = quantity_id
        self.string_id = string_id

    def __repr__(self):
        return '<Quantity {}>'.format(self.name)

    @property
    def name(self):
        """
        Get the (localized) display name of the quantity.
        """
        return self.display_name.value


@event.listens_for(Quantity.__table__, 'after_create')
def _default_quantities(target, connection, *args, **kwargs):  # pylint: disable=unused-argument
    session = Session(bind=connection)
    session.add(Quantity(0, 'GUI_MACHINE_CRAFT_TAB_SINGLE'))
    session.add(Quantity(1, 'GUI_MACHINE_CRAFT_TAB_BULK'))
    session.add(Quantity(2, 'GUI_MACHINE_CRAFT_TAB_MASS'))
    session.commit()
