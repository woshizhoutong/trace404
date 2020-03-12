from db.db_setup import Base, engine, db_session
from models.models import CoronaVirusData, News
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import text
from cachetools import cached, LRUCache, TTLCache


def save_corona_virus_data(data_items, source_file_published_date, is_today=False):
    items = []
    today = 'today' if is_today else 'yesterday'
    for data_item in data_items:
        entry = {
            "id": data_item.country + "|" + data_item.state + "|" + today,
            "country": data_item.country,
            "state": data_item.state,
            "state_name": data_item.state_name,
            "confirmed_case": data_item.confirmed_case,
            "recovered_case": data_item.recovered_case,
            "death_case": data_item.death_case,
            "is_today": is_today,
            "source_file_published_date": source_file_published_date,
        }
        items.append(entry)
    insert_stmt = insert(CoronaVirusData).values(items)

    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
        confirmed_case=insert_stmt.inserted.confirmed_case,
        recovered_case=insert_stmt.inserted.recovered_case,
        death_case=insert_stmt.inserted.death_case,
        source_file_published_data=insert_stmt.inserted.source_file_published_date)
    with engine.connect() as conn:
        conn.execute(on_duplicate_key_stmt)


def retrieve_all_corona_virus_data(is_today):
    sql = text("select * from data_items where is_today = :is_today")
    with engine.connect() as conn:
        result = conn.execute(sql, is_today=is_today).fetchall()
        return result


def retrieve_last_updated_time_corona_virus_data():
    with engine.connect() as conn:
        rows = conn.execute("""
            SELECT source_file_published_date
            FROM   data_items
            limit 1
           """).fetchall()
        # timestamp is in second
        if rows and rows[0]['source_file_published_date']:
            return rows[0]['source_file_published_date']
        else:
            return None


def save_news_list(news_list):
    l = []
    for news in news_list:
        entry = {
            "id": news.id,
            "url": news.url,
            "title": news.title,
            "img_url": news.img_url,
            "description": news.description,
            "publishedAt": news.publishedAt,
            "source": news.source,
            "content": news.content,
        }
        l.append(entry)
    insert_stmt = insert(News).values(l)

    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(url=insert_stmt.inserted.url)
    with engine.connect() as conn:
        conn.execute(on_duplicate_key_stmt)


def save_news_content_list(news_content_list):
    for news_content in news_content_list:
        db_session.merge(news_content)
    # Save all pending changes to the database

    db_session.commit()


@cached(cache=TTLCache(maxsize=2048, ttl=600))
def retrieve_news_by_id(news_id):
    sql = text("select * from news where id = :news_id")
    with engine.connect() as conn:
        result = conn.execute(sql, news_id=news_id).fetchall()
        return result
