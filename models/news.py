from flask import Flask, Response
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException
from sqlalchemy import Column, String, Integer
import attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///news.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@attr.s
class News(object):
    id = attr.ib()
    title = attr.ib()
    url = attr.ib()
    img_url = attr.ib()
    description = attr.ib()
    publishedAt = attr.ib()
    source = attr.ib()


def create_news(data_item):
    return News(
        id=data_item['url'],
        title=data_item['title'],
        url=data_item['url'],
        img_url=data_item['urlToImage'],
        description=data_item['description'],
        publishedAt=data_item['publishedAt'],
        source=data_item['source']['name'])
