from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from app.config import config

engine = create_engine(config.DATABASE_URL)

Base = declarative_base()
