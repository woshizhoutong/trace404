from flask import Flask, Response
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///news.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

import attr

@attr.s
class News(object):
    id = attr.ib()
    title = attr.ib()
    url = attr.ib()
    img_url = attr.ib()
    description = attr.ib()
    publishedAt = attr.ib()
    source = attr.ib()