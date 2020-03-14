import datetime
import re
import logging

from cachetools import cached, LRUCache, TTLCache
from newsapi.newsapi_exception import NewsAPIException

from models.models import News
from newsapi import NewsApiClient
from service import db_service

log = logging.getLogger(__name__)

# Init
newsapi_clients = [NewsApiClient(api_key='7729d579e9b049c084574a43f35369b3')]

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}


def read_all_serving_news(state):
    return db_service.retrieve_all_serving_news(state)


def update_news(query, country):
    from_date = datetime.datetime.now().strftime("%Y-%m-%d")
    to_date = datetime.datetime.now().strftime("%Y-%m-%d")

    log.info("Clearing all serving news, set their rank to 0. The newly read news from newsapi will be served")
    db_service.clear_all_serving_news()

    log.info("Reading usa country wise news")
    _read_from_news_api(query=query,
                        from_date=from_date,
                        to_date=to_date,
                        state=country,
                        country=country)

    log.info("Reading usa country state wise news")
    query_for_all_states = ""
    for state in us_state_abbrev.keys():
        query_for_all_states += ' OR (' + state + ')'
    query_for_all_states = query_for_all_states[4:]
    _read_from_news_api(query='', from_date=from_date, to_date=to_date,
                        query_in_title=query + ' AND (' + query_for_all_states + ')')


def _find_matching_state(articles_item):
    for state in us_state_abbrev.keys():
        pattern = '.*' + state + '.*'
        if re.match(pattern, articles_item['title']):
            print('matching state ', state)
            return state
    return None


def _read_from_news_api(query, from_date, to_date, query_in_title=None, state='', country=''):
    for client in newsapi_clients:
        try:
            if query_in_title:
                response = client.get_everything(qintitle=query_in_title,
                                                 from_param=from_date,
                                                 to=to_date,
                                                 language='en',
                                                 sort_by='relevancy')
            else:
                response = client.get_everything(q=query,
                                                 from_param=from_date,
                                                 to=to_date,
                                                 language='en',
                                                 sort_by='relevancy')
            news_list = []
            for item in response['articles']:
                # filter the news if no image to show
                if item['urlToImage']:
                    log.info("News without image_url filtered, {news_id}.".format(news_id=item['url']))
                    state = _find_matching_state(item)
                    news_list.append(_create_news(item, state, country))
                    db_service.save_news_list(news_list)
            return
        except NewsAPIException as e:
            log.warning("NewsApi threw exception {e}, The client api-key is {client}. ".format(e=str(e), client=str(
                client.auth.api_key)))
            continue


def _create_news(data_item, state, country):
    return News(
        id=data_item['url'],
        title=data_item['title'],
        url=data_item['url'],
        img_url=data_item['urlToImage'],
        description=data_item['description'],
        publishedAt=data_item['publishedAt'],
        source=data_item['source']['name'],
        content=data_item['content'],
        state=state,
        country=country
    )
