import datetime
import logging

from cachetools import cached, LRUCache, TTLCache
from newsapi.newsapi_exception import NewsAPIException

from models.models import News
from newsapi import NewsApiClient
from service import db_service
import itertools
from hashlib import sha256

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
    'Northern Mariana Islands':'MP',
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

    _update_country_news(query, from_date, to_date, country)
    state_list = list(us_state_abbrev.keys())
    for i in range(0, 3):
        state_list_sub = state_list[i*20:i*20+20]
        _update_state_news(query, from_date, to_date, country, state_list_sub)


def _update_state_news(query, from_date, to_date, country, state_list):
    log.info("Reading usa country state wise news for {state_list}".format(state_list=state_list))
    delimiter = ' OR '
    state_query_str = delimiter.join('"' + item + '"' for item in state_list)
    state_query_str = query + ' AND (' + state_query_str + ')'

    log.info("Reading usa country state wise news.")
    item_list = []
    response = _read_from_news_api(query='', from_date=from_date, to_date=to_date,
                                   query_in_title=state_query_str)
    item_list.extend(response['articles'])
    log.info("There are totally {count} number of results".format(count=response['totalResults']))

    response = _read_from_news_api(query='', from_date=from_date, to_date=to_date,
                                   query_in_title=state_query_str)
    item_list.extend(response['articles'])

    state_news_list_map = dict.fromkeys(state_list, [])
    filtered_news_counter = 0
    for item in item_list:
        # filter the news if no image to show
        if not item['urlToImage']:
            filtered_news_counter += 1
            continue

        for state_name in state_news_list_map.keys():
            if state_name in item['title']:
                news = _create_news(item, state=us_state_abbrev[state_name], country=country)
                state_news_list_map[state_name].append(news)

    log.info("{counter} number of news are filtered.".format(counter=filtered_news_counter))

    flat_news_list = list(itertools.chain.from_iterable(state_news_list_map.values()))
    if flat_news_list:
        db_service.save_news_list(flat_news_list)


def _update_country_news(query, from_date, to_date, country):
    log.info("Reading usa country wise news")
    response = _read_from_news_api(query=query,
                                   from_date=from_date,
                                   to_date=to_date)
    news_list = []
    for item in response['articles']:
        # filter the news if no image to show
        if item['urlToImage']:
            news_list.append(_create_news(item, country, country))
            db_service.save_news_list(news_list)


def _read_from_news_api(query, from_date, to_date, query_in_title=None, page_size=100):
    for client in newsapi_clients:
        try:
            if query_in_title:
                response = client.get_everything(qintitle=query_in_title,
                                                  from_param=from_date,
                                                  to=to_date,
                                                  language='en',
                                                  sort_by='popularity',
                                                 page_size=page_size)
            else:
                response = client.get_everything(q=query,
                                                  from_param=from_date,
                                                  to=to_date,
                                                  language='en',
                                                  sort_by='relevancy')

            return response
        except NewsAPIException as e:
            log.warning("NewsApi threw exception {e}, The client api-key is {client}. ".format(e=str(e), client=str(client.auth.api_key)))
            continue


def _create_news(data_item, state, country):
    news_id = sha256((data_item['url'] + state + country).encode('utf-8')).hexdigest()
    return News(
        id=news_id,
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
