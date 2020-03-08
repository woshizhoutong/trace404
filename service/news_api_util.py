from cachetools import cached, LRUCache, TTLCache
from models.models import create_news
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
        news_list.append(create_news(item))

    return news_list