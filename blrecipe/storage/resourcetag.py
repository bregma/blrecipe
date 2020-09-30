"""
Resource Tags
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class ResourceTag(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting Items
    """

    __tablename__ = 'ResourceTag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    string_id = Column(String(64), ForeignKey('Translation.string_id'))
    found_altitude = Column(String(64), nullable=False)
    found_depth = Column(String(64), nullable=False)
    found_material = Column(String(64), nullable=False)

    translation = relationship('Translation', foreign_keys=[string_id])

    def __init__(self, string_id, found_altitude, found_depth, found_material, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string_id = string_id
        self.found_altitude = found_altitude
        self.found_depth = found_depth
        self.found_material = found_material

    def __repr__(self):
        return '<ResourceTag {} (alt={} depth={} mat={})>'.format(
            self.string_id,
            self.found_altitude,
            self.found_depth,
            self.found_material,
        )

    @property
    def display_name(self):
        """
        Get the (localized) display name of the item.
        """
        return self.translation.value if self.translation else "unknown"

