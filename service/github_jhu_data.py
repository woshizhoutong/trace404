import base64
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO

import requests
import json
from cachetools import cached, TTLCache
from github import Github
import os.path
from models.models import CoronaVirusData
from shutil import copyfile
from flask import current_app
from service import db_service

g = Github("tobyzhoudevelop", "Twofactorauthentication1234")
repo = g.get_repo('CSSEGISandData/COVID-19')
data_directory_template = '/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv'


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


def read_data_from_github(data_directory):
    try:
        print("Reading data in Github at {path}".format(path=data_directory))
        contents = repo.get_contents(data_directory)
        data = contents.decoded_content.decode('UTF-8')
        f = StringIO(data)
        reader = csv.DictReader(f)
        rows = list(reader)
    except Exception as e:
        print("Something wrong reading github at {path}. {error}".format(path=data_directory, error=str(e)))
        raise e

    data_map = {}
    for row in rows:
        country = row['Country/Region']
        if country == 'US':
            # if confirmed from diamond princess, JHU mark it with (From Diamond Princess)
            if "," not in row['Province/State'] and row['Province/State'].strip() in us_state_abbrev:
                state = us_state_abbrev[row['Province/State'].strip()]
            elif "," in row['Province/State']:
                state = row['Province/State'].split(',')[1].strip()
            else:
                state = 'other'

            if state in data_map:
                data = data_map[state]
                data.confirmed_case += int(row['Confirmed'])
                data.death_case += int(row['Deaths'])
                data.recovered_case += int(row['Recovered'])
            else:
                data = CoronaVirusData(id='', country=country, state=state, state_name='',
                                       confirmed_case=int(row['Confirmed']), death_case=int(row['Deaths']),
                                       recovered_case=int(row['Recovered']))
                data_map[state] = data

    return data_map


# memoize ttl in seconds.
@cached(cache=TTLCache(maxsize=2048, ttl=300))
def read_usa_daily_report():
    """
    :return: A tuple, which contains  list of CoronaVirusData, and last_updated_at.
    """
    return db_service.retrieve_all_corona_virus_data(is_today=True), db_service.retrieve_last_updated_time_corona_virus_data()


def daily_data_process():
    for i in range(0, 2):
        todays_date = datetime.now().date() - timedelta(days=i)
        todays_date_str = todays_date.strftime("%m-%d-%Y")
        today_data_directory = data_directory_template.format(date=todays_date_str)

        yesterday_date = todays_date - timedelta(days=1)
        yesterday_date_str = yesterday_date.strftime("%m-%d-%Y")
        yesterday_data_directory = data_directory_template.format(date=yesterday_date_str)

        # last_updated_time type is last_updated_time
        last_updated_time = db_service.retrieve_last_updated_time_corona_virus_data()
        if last_updated_time and last_updated_time.date() >= todays_date:
            print("Not Reading data in Github at {path}. Current version at {last_updated_time} is newer".format(
                path=today_data_directory, last_updated_time=last_updated_time))
            return

        try:
            data_map = read_data_from_github(today_data_directory)
            # save the date on the filename in github as published_date, it would be easy to compare later
            datetime_to_todays_midnight = datetime.combine(todays_date, datetime.min.time())
            db_service.save_corona_virus_data(data_map.values(), datetime_to_todays_midnight, isToday=True)

            data_map = read_data_from_github(yesterday_data_directory)
            db_service.save_corona_virus_data(data_map.values(), datetime_to_todays_midnight, isToday=False)
            return
        except Exception as e:
            print(e)


def compute_data_delta():
    today_data_items = db_service.retrieve_all_corona_virus_data(is_today=True)
    yesterday_data_items = db_service.retrieve_all_corona_virus_data(is_today=False)

    yesterday_data_map = {}
    for yesterday_data_item in yesterday_data_items:
        yesterday_data_map[yesterday_data_item.state] = yesterday_data_item

    data_delta_map = {}
    for today_date_item in today_data_items:
        if today_date_item.state in yesterday_data_map:
            data_delta_map[today_date_item.state] = get_data_delta(today_date_item, yesterday_data_map[today_date_item.state])
        else:
            empty_yesterday_data = CoronaVirusData(
                id='',
                country=today_date_item.country,
                state=today_date_item.state,
                state_name=today_date_item.state_name,
                confirmed_case=0,
                recovered_case=0,
                death_case=0,
            )
            data_delta_map[today_date_item.state] = get_data_delta(today_date_item, empty_yesterday_data)

    return data_delta_map.values()


def get_data_delta(cvd_1, cvd_2):
    return CoronaVirusData(id='', country=cvd_1.country, state=cvd_1.state, state_name=cvd_1.state_name,
                           confirmed_case=cvd_1.confirmed_case - cvd_2.confirmed_case,
                           recovered_case=cvd_1.recovered_case - cvd_2.recovered_case,
                           death_case=cvd_1.death_case - cvd_2.death_case)
