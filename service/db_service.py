from datetime import timezone

from db.db_setup import Base, engine, db_session
from models.models import CoronaVirusData, News, NewsContent


def save_corona_virus_data(data_item):
    id = data_item.country + "|" + data_item.state
    with engine.connect() as conn:
        conn.execute("""
            INSERT INTO data_items (id, country, state, state_name, confirmed_case, recovered_case, death_case)
            VALUES ("{id}", "{country}", "{state}", "{state_name}", "{confirmed_case}", "{recovered_case}", "{death_case}")
            ON DUPLICATE KEY UPDATE
            confirmed_case="{confirmed_case}",
            recovered_case="{recovered_case}",
            death_case="{death_case}",
            source_file_published_date="{source_file_published_date}"
        """.format(id=id,
                   country=data_item.country,
                   state=data_item.state,
                   state_name=data_item.state_name,
                   confirmed_case=data_item.confirmed_case,
                   recovered_case=data_item.recovered_case,
                   death_case=data_item.death_case,
                   source_file_published_date=data_item.source_file_published_date)
        )
        return 'save_done'

def retrieve_all_corona_virus_data():
    data_items = db_session.query(CoronaVirusData).all()
    return data_items


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
    for news in news_list:
        db_session.merge(news)
    # Save all pending changes to the database
    db_session.commit()


def save_news_content_list(news_content_list):
    for news_content in news_content_list:
        db_session.merge(news_content)
    # Save all pending changes to the database

    db_session.commit()


def retrieve_news_by_id(news_id):
    results = db_session.query(News).filter(News.id == news_id).all()
    return results


def retrieve_news_content_by_id(news_id):
    results = db_session.query(NewsContent).filter(News.id == news_id).all()
    return results
