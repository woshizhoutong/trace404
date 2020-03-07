from datetime import datetime, timezone

import sqlalchemy

from models.corona_virus_data import CoronaVirusData


cloud_sql_connection_name = 'ordinal-avatar-270006:us-central1:trace404-sql-data'

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='mysql+pymysql',
        username='root',
        password='',
        database='trace404',
        query={
            'unix_socket': '/cloudsql/{}'.format(cloud_sql_connection_name)
        }
    ),
    # ... Specify additional properties here.
    # ...
)

# uncomment the following setting for local test.

# credentials = {
#     'username': 'root',
#     'password': 'my-secret-pw',
#     'host': '127.0.0.1',
#     'database': 'db_test',
#     'port': '3306'}
#
# db_user = credentials.get('username')
# db_pwd = credentials.get('password')
# db_host = credentials.get('host')
# db_port = credentials.get('port')
# db_name = credentials.get('database')
#
# connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
# engine = sqlalchemy.create_engine(connection_str)
# db = engine.connect()

def create_tables():
# Create tables (if they don't already exist)
    with db.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id varchar(255),
                title varchar(255),
                url varchar(255),
                img_url varchar(255),
                description varchar (255),
                publishedAt varchar(255),
                source varchar(255),
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data_items (
                id varchar(255),
                country varchar(255),
                state varchar(255),
                state_name varchar(255),
                confirmed_case varchar (255),
                recovered_case varchar(255),
                death_case varchar(255),
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            );
            """
        )


def save_corona_virus_data(data_item):
    id = data_item.country + "|" + data_item.state
    with db.connect() as conn:
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
    with db.connect() as conn:
        rows = conn.execute("""
            SELECT id, country, state, state_name, confirmed_case, recovered_case, death_case 
            FROM data_items
        """
        ).fetchall()

        data_items = []
        for row in rows:
            data_item = CoronaVirusData(id=row['id'], country=row['country'], state=row['state'], state_name=row['state_name'], confirmed_case=int(row['confirmed_case']), death_case=int(row['death_case']), recovered_case=int(row['recovered_case']))
            data_items.append(data_item)

        return data_items


def retrieve_last_updated_time_corona_virus_data():
    with db.connect() as conn:
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
