from sqlalchemy import create_engine

from ntm.config import SQLITE_DB

engine = create_engine(SQLITE_DB, echo=True)
