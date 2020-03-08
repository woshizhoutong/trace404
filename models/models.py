from db.db_setup import Base, engine
from sqlalchemy import Column, String, Integer, TIMESTAMP, text


class CoronaVirusData(Base):
    __tablename__ = 'data_items'
    id = Column(String(255), primary_key=True)
    country = Column(String(255))
    state = Column(String(255))
    state_name = Column(String(255))
    confirmed_case = Column(Integer)
    recovered_case = Column(Integer)
    death_case = Column(Integer)
    last_update = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class News(Base):
    __tablename__ = 'news'
    id = Column(String(255), primary_key=True)
    title = Column(String(255))
    url = Column(String(255))
    img_url = Column(String(255))
    description = Column(String(5000))
    publishedAt = Column(String(255))
    source = Column(String(255))


def create_news(data_item):
    return News(
        id=data_item['url'],
        title=data_item['title'],
        url=data_item['url'],
        img_url=data_item['urlToImage'],
        description=data_item['description'],
        publishedAt=data_item['publishedAt'],
        source=data_item['source']['name'])


print("Creating database tables...")
Base.metadata.create_all(engine)
print("Done!")
