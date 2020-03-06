import base64
import csv
from datetime import datetime, timedelta
from io import StringIO

import requests
import json
from cachetools import cached, TTLCache
from github import Github
import os.path
from models.corona_virus_data import CoronaVirusData
from shutil import copyfile
from flask import current_app


g = Github("tobyzhoudevelop", "Twofactorauthentication1234")
repo = g.get_repo('CSSEGISandData/COVID-19')
data_directory_template = '/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv'
local_data_dir_prefix = 'static/data'
today_daily_report_dir = 'static/data/today_daily_report.csv'

# memoize ttl in seconds.
@cached(cache=TTLCache(maxsize=2048, ttl=300))
def read_usa_daily_report():
    """
    :return: A tuple, which contains  list of CoronaVirusData, and last_updated_at.
    """
    if os.path.isfile(today_daily_report_dir):
        # Last modified time in seconds, convert it to ms.
        last_updated_at = os.path.getmtime(today_daily_report_dir) * 1000
        with open(today_daily_report_dir) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # format of row:
        # OrderedDict(
        #     [('Province/State', 'San Mateo, CA'), ('Country/Region', 'US'), ('Last Update', '2020-03-03T00:43:02'),
        #      ('Confirmed', '2'), ('Deaths', '0'), ('Recovered', '0'), ('Latitude', '37.5630'),
        #      ('Longitude', '-122.3255')])
        data_map = {}
        for row in rows:
            country = row['Country/Region']
            if country == 'US':
                # if confirmed from diamond princess, JHU mark it with (From Diamond Princess)
                if "(From Diamond Princess)" in row['Province/State']:
                    state = "diamond_princess"
                else:
                    state = row['Province/State'].split(',')[1].strip()
                if state in data_map:
                    data = data_map[state]
                    data.confirmed_case += int(row['Confirmed'])
                    data.death_case += int(row['Deaths'])
                    data.recovered_case += int(row['Recovered'])
                else:
                    data = CoronaVirusData(id='', country=country, state=state, state_name='', confirmed_case=int(row['Confirmed']), death_case=int(row['Deaths']), recovered_case=int(row['Recovered']))
                    data_map[state] = data

        return data_map.values(), last_updated_at
    else:
        print("cannot find file at {dir}".format(dir=today_daily_report_dir))
        return ''


def daily_data_process():
    for i in range(0, 5):
        date = datetime.now() - timedelta(days=i)
        todays_date = date.strftime("%m-%d-%Y")
        data_directory = data_directory_template.format(date=todays_date)

        if os.path.isfile(local_data_dir_prefix + data_directory):
            if not os.path.isfile(today_daily_report_dir):
                copyfile(local_data_dir_prefix + data_directory, today_daily_report_dir)
            return

        try:
            print("Reading data in Github at {path}".format(path=data_directory))
            contents = repo.get_contents(data_directory)
            data = contents.decoded_content.decode('UTF-8')
            f = StringIO(data)
            reader = csv.DictReader(f)
            rows = list(reader)

            with open(local_data_dir_prefix + data_directory, mode='w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(dict(rows[0]))
                for row in rows:
                    writer.writerow(dict(row).values())

            with open(today_daily_report_dir, "w") as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow(dict(rows[0]))
                for row in rows:
                    writer.writerow(dict(row).values())
            return
        except Exception as e:
            print("Something wrong reading github at {path}. {error}".format(path=data_directory, error=str(e)))
