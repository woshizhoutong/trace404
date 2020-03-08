from datetime import timezone

from db.db_setup import Base, engine, db_session
from models.models import CoronaVirusData


def save_corona_virus_data(data_item):
    id = data_item.country + "|" + data_item.state
    with engine.connect() as conn:
        conn.execute("""
            INSERT INTO data_items (id, country, state, state_name, confirmed_case, recovered_case, death_case)
            VALUES ("{id}", "{country}", "{state}", "{state_name}", "{confirmed_case}", "{recovered_case}", "{death_case}")
            ON DUPLICATE KEY UPDATE
            confirmed_case="{confirmed_case}",
            recovered_case="{recovered_case}",
            death_case="{death_case}"
        """.format(id=id,
                   country=data_item.country,
                   state=data_item.state,
                   state_name=data_item.state_name,
                   confirmed_case=data_item.confirmed_case,
                   recovered_case=data_item.recovered_case,
                   death_case=data_item.death_case)
        )
        return 'save_done'

def retrieve_all_corona_virus_data():
    data_items = db_session.query(CoronaVirusData).all()
    return data_items


def retrieve_last_updated_time_corona_virus_data():
    with engine.connect() as conn:
        rows = conn.execute("""
            SELECT last_update
            FROM   data_items
            limit 1
           """).fetchall()
        # timestamp is in second
        if rows and rows[0]['last_update']:
            return rows[0]['last_update'].replace(tzinfo=timezone.utc).timestamp()
        else:
            return None


def save_news(news):
    db_session.merge(news)

    # Save all pending changes to the database
    db_session.commit()


def retrieve_news(news_id):
    with engine.connect() as conn:
        rows = conn.execute("""
            SELECT *
            FROM news
            WHERe id={id}
        """.format(id=news_id)
        )
        if rows:
            return rows[0]