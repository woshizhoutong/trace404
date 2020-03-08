import base64
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO

import requests
import json
from cachetools import cached, TTLCache
from github import Github
import os.path
from models.corona_virus_data import CoronaVirusData, get_data_delta
from shutil import copyfile
from flask import current_app
from db import db_setup

g = Github("tobyzhoudevelop", "Twofactorauthentication1234")
repo = g.get_repo('CSSEGISandData/COVID-19')
data_directory_template = '/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv'


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

    data_map = {}
    for row in rows:
        country = row['Country/Region']
        if country == 'US':
            # if confirmed from diamond princess, JHU mark it with (From Diamond Princess)
            if "(From Diamond Princess)" in row['Province/State']:
                state = "diamond_princess"
            elif "Grand Princess Cruise Ship" == row['Province/State']:
                state = "grand_princess"
            else:
                print(row['Province/State'])
                state = row['Province/State'].split(',')[1].strip()
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
    return db_setup.retrieve_all_corona_virus_data(), db_setup.retrieve_last_updated_time_corona_virus_data()


def daily_data_process():
    # daily_data_delta_process()
    for i in range(0, 2):
        date = datetime.now() - timedelta(days=i)
        todays_date = date.strftime("%m-%d-%Y")
        data_directory = data_directory_template.format(date=todays_date)

        last_updated_time = db_setup.retrieve_last_updated_time_corona_virus_data()
        if last_updated_time and datetime.fromtimestamp(last_updated_time).date() >= date.date():
            print("Not Reading data in Github at {path}. Current version at {last_updated_time} is newer".format(
                path=data_directory, last_updated_time=last_updated_time))
            return
        try:
            data_map = read_data_from_github(data_directory)
        except Exception as e:
            continue

        for data in data_map.values():
            db_setup.save_corona_virus_data(data)


def get_today_yesterday_data():
    today_date = datetime.fromtimestamp(db_setup.retrieve_last_updated_time_corona_virus_data())
    yesterday_date = today_date - timedelta(days=1)
    today_data = read_data_from_github(data_directory_template.format(date=today_date.strftime(
        "%m-%d-%Y")))
    yesterday_data = read_data_from_github(data_directory_template.format(date=yesterday_date.strftime(
        "%m-%d-%Y")))

    return today_data, yesterday_data


def compute_data_delta():
    today_data, yesterday_data = get_today_yesterday_data()
    data_delta_map = {}
    for data in today_data.values():
        if data.state in yesterday_data.keys():
            data_delta_map[data.state] = get_data_delta(data, yesterday_data[data.state])
        else:
            empty_yesterday_data = CoronaVirusData(
                id='',
                country=data.country,
                state=data.state,
                state_name=data.state_name,
                confirmed_case=0,
                recovered_case=0,
                death_case=0,
            )
            data_delta_map[data.state] = get_data_delta(data, empty_yesterday_data)

    return data_delta_map
