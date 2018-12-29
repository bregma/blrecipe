"""
Quantity Classifications
"""

from sqlalchemy import Column, Integer, String, event, DDL
from .database import BaseObject


class Quantity(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of recipe quantities
    """

    __tablename__ = 'Quantity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(8), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.display_name


event.listen(Quantity.__table__, 'after_create',  # pylint: disable=no-member
             DDL("""INSERT INTO Quantity (display_name) VALUES ('Single'), ('Bulk'), ('Mass');"""))
