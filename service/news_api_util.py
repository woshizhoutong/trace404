from urllib.parse import quote

import requests
import json
from cachetools import cached, LRUCache, TTLCache

from service import db_service
from models.models import News
import uuid
from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='58d7c8cd9cf14565a96c1a7a73ba7611')


# memoize ttl in seconds.
@cached(cache=TTLCache(maxsize=2048, ttl=3600))
def read_from_news_api(query, from_date, to_date, query_in_title):

    if query_in_title:
        response = newsapi.get_everything(qintitle=query_in_title,
                                          from_param=from_date,
                                          to=to_date,
                                          language='en',
                                          sort_by='relevancy')
    else:
        response = newsapi.get_everything(q=query,
                                          from_param=from_date,
                                          to=to_date,
                                          language='en',
                                          sort_by='relevancy')

    news_list = []
    for item in response['articles']:
        news = News(
            id=item['url'],
            title=item['title'],
            url=item['url'],
            img_url=item['urlToImage'],
            description=item['description'],
            publishedAt=item['publishedAt'],
            source=item['source']['name']
        )
        db_service.save_news(news)
        news_list.append(news)

    return news_list

