"""
Machine Definitions
"""

from sqlalchemy import Column, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from .database import BaseObject, Session


class Machine(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting machines
    """

    __tablename__ = 'Machine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(16), nullable=False)
    string_id = Column(String(64), ForeignKey('Translation.string_id'), nullable=False)
    translation = relationship('Translation')

    def __init__(self, name, string_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.string_id = string_id

    def __repr__(self):
        return self.string_id

    @property
    def display_name(self):
        """Get the (localized) display name of the machine."""
        return self.translation.value if self.translation else self.string_id

@event.listens_for(Machine.__table__, 'after_create')
def _default_quantities(target, connection, **kw):  # pylint: disable=unused-argument
    session = Session(bind=connection)
    session.add(Machine('CRAFTING_TABLE', 'GUI_CRAFTING_TABLE_TITLE'))
    session.add(Machine('WORKBENCH', 'GUI_MACHINE_WORKBENCH_TITLE'))
    session.add(Machine('EXTRACTOR', 'GUI_MACHINE_EXTRACTOR_TITLE'))
    session.add(Machine('COMPACTOR', 'GUI_MACHINE_COMPACTOR_TITLE'))
    session.add(Machine('REFINERY', 'GUI_MACHINE_REFINERY_TITLE'))
    session.add(Machine('MIXER', 'GUI_MACHINE_MIXER_TITLE'))
    session.add(Machine('FORGE', 'GUI_MACHINE_FORGE_TITLE'))
    session.add(Machine('FURNACE', 'GUI_MACHINE_FURNACE_TITLE'))
    session.add(Machine('POWERCORE', 'GUI_MACHINE_POWERCORE_TITLE'))
    session.add(Machine('HELIX', 'GUI_MACHINE_HELIX_TITLE'))
    session.add(Machine('DYE_MAKER', 'GUI_DYE_MAKER_TITLE'))
    session.commit()
