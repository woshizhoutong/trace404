from datetime import datetime, timezone

import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

cloud_sql_connection_name = 'trace404:us-west2:trace404'

engine = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='mysql+pymysql',
        username='root',
        password='',
        database='trace404_prod',
        query={
            'unix_socket': '/cloudsql/{}'.format(cloud_sql_connection_name)
        }
    ),
    # ... Specify additional properties here.
    # ...
)

# uncomment the following setting for local test.

credentials = {
    'username': 'root',
    'password': 'hahaha',
    'host': '127.0.0.1',
    'database': 'db_test',
    'port': '3306'}

db_user = credentials.get('username')
db_pwd = credentials.get('password')
db_host = credentials.get('host')
db_port = credentials.get('port')
db_name = credentials.get('database')

connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
engine = sqlalchemy.create_engine(connection_str)
db = engine.connect()

# uncomment the setting for local test.

Base = declarative_base()
Base.metadata.bind = engine

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

