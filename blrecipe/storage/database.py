"""
The database isolation layer
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# A base class for all data models cached in persisten storage
BaseObject = declarative_base()  # pylint: disable=invalid-name

# Global factory object for creating sessions
Session = sessionmaker()  # pylint: disable=invalid-name


class Database(object):  #pylint: disable=too-few-public-methods
    """
    Encapsulate the RDBMS used as a persistent store
    """

    def __init__(self):
#        self._engine = create_engine("sqlite:///blrecipe.db", echo="debug")
        self._engine = create_engine("sqlite:///blrecipe.db")
        self._connection = self._engine.connect()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        insp = inspect(self._engine)
        if 'Machine' not in insp.get_table_names():
            BaseObject.metadata.create_all(self._engine)

    def session(self):
        """
        Get a database session
        """
        return Session(bind=self._connection)

    def close(self):
        """
        Tear down the database connection
        """
        self._connection.close()
