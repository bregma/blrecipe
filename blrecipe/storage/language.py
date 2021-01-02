"""
Supported Languages

Boundless supports localization in a number if languages. These languages are
enumerated in the itemcolorstrings.dat file.
"""

from sqlalchemy import Column, Integer, String
from .database import BaseObject


class Language(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Languages supported for in-gam localization
    """

    __tablename__ = 'Language'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(32), nullable=False)

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

