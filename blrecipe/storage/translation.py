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
    lang = Column(String(32), nullable=False)
    string_id = Column(String(64), nullable=False)
    value = Column(String(255), nullable=False)

    def __init__(self, string_id, lang=None, value=None):
        self.lang = 'english' if lang is None else lang
        self.string_id = string_id
        self.value = string_id if value is None else value


def i18n(session, string_id):
    """
    Return the internationalized translation of a key string
    """
    return session.query(Translation).filter_by(string_id=string_id).first().value


class ItemName(BaseObject):   # pylint: disable=too-few-public-methods
    """
    Item name localization table

    The developers switched from using the "strings" translation for items to
    using the itemcolorstring translation.
    """
    __tablename__ = 'ItemName'
    __table_args__ = (UniqueConstraint('lang', 'item_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    lang = Column(String(32), nullable=False)
    item_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    subtitle = Column(String(255))

    def __init__(self, item_id, lang=None, name=None, subtitle=None):
        self.lang = 'english' if lang is None else lang
        self.item_id = item_id
        self.name = "[item {}]".format(item_id) if name is None else name
        self.subtitle = subtitle


class MetalName(BaseObject):   # pylint: disable=too-few-public-methods
    """
    Metal name localization table
    """
    __tablename__ = 'MetalName'
    __table_args__ = (UniqueConstraint('lang', 'metal_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    lang = Column(String(32), nullable=False)
    metal_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)

    def __init__(self, metal_id, lang=None, name=None):
        self.lang = 'english' if lang is None else lang
        self.metal_id = metal_id
        self.name = "[metal {}]".format(metal_id) if name is None else name

