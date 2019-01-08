"""
I18N translations
"""

from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import BaseObject


class Translation(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A string translation table
    """
    __tablename__ = 'Translation'
    __table_args__ = (UniqueConstraint('lang', 'string_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    lang = Column(String(2), nullable=False)
    string_id = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

    def __init__(self, string_id, lang=None, value=None, *args, **kwargs):
        self.lang = 'en' if lang is None else lang
        self.string_id = string_id
        self.value = string_id if value is None else value
