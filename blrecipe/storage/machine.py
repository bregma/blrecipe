"""
Machine Definitions
"""

from sqlalchemy import Column, Integer, String, event, DDL
from .database import BaseObject


class Machine(BaseObject):  # pylint: disable=too-few-public-methods
    """
    A defined set of crafting machines
    """

    __tablename__ = 'Machine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(16), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.display_name


event.listen(Machine.__table__, 'after_create',  # pylint: disable=no-member
             DDL("""INSERT INTO Machine (display_name)
                        VALUES ('Crafting Table'),
                               ('Workbench'),
                               ('Extractor'),
                               ('Compactor'),
                               ('Refinery'),
                               ('Mixer'),
                               ('Centraforge'),
                               ('Furnace');"""))
