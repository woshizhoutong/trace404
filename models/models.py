import logging

from db.db_setup import Base, engine
from sqlalchemy import Column, String, Integer, TIMESTAMP, text, Text, Boolean

log = logging.getLogger('__main__')

class CoronaVirusData(Base):
    __tablename__ = 'data_items'
    id = Column(String(255), primary_key=True)
    country = Column(String(255))
    state = Column(String(255))
    state_name = Column(String(255))
    confirmed_case = Column(Integer)
    recovered_case = Column(Integer)
    death_case = Column(Integer)
    is_today = Column(Boolean)
    last_update = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    source_file_published_date = Column(TIMESTAMP)


class News(Base):
    __tablename__ = 'news'
    id = Column(String(255), primary_key=True)
    title = Column(String(255))
    url = Column(String(255))
    img_url = Column(String(1024))
    description = Column(String(2048))
    publishedAt = Column(String(255))
    source = Column(String(255))
    content = Column(String(4096))
    category = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))
    rank_value = Column(Integer)
    last_update = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

log.info("Creating database tables...")
Base.metadata.create_all(engine)
log.info(print("Done!"))
