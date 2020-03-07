#!/usr/bin/env python
import csv
import json
import os
import flask
import datetime

import sqlalchemy

from service import news_api_util
from service import github_jhu_data
from apscheduler.schedulers.background import BackgroundScheduler
from db import db_setup

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template('index.html')


@app.route("/coronavirus")
def coronavirus():
    return flask.render_template('index.html')


@app.route("/news")
def get_news():
    query = flask.request.args.get('q')
    query_in_title = flask.request.args.get('query_in_title', '')
    from_date = datetime.datetime.now().strftime("%Y-%m-%d")
    to_date = datetime.datetime.now().strftime("%Y-%m-%d")

    news_list = news_api_util.read_from_news_api(query=query, from_date=from_date, to_date=to_date, query_in_title=query_in_title)
    json_string = json.dumps([vars(ob) for ob in news_list])
    return json_string


@app.route("/today_usa_data")
def get_today_usa_data():
    data_list, last_updated_at = github_jhu_data.read_usa_daily_report()
    sum_of_confirmed = 0
    sum_of_death = 0
    sum_of_recovered = 0

    for data in data_list:
        sum_of_confirmed += data.confirmed_case
        sum_of_death += data.death_case
        sum_of_recovered += data.recovered_case

    response = {
        'sum_of_confirmed': sum_of_confirmed,
        'sum_of_death': sum_of_death,
        'sum_of_recovered': sum_of_recovered,
        'data': [vars(ob) for ob in data_list],
        # times 1000 to change the time to milliseconds
        'last_updated_at': last_updated_at * 1000
    }
    json_string = json.dumps(response)
    return json_string


def corona_virus_data_process():
    print('Loading daily report from github.')
    github_jhu_data.daily_data_process()


    # id = attr.ib()
    # country = attr.ib()
    # state = attr.ib()
    # state_name = attr.ib()
    # confirmed_case = attr.ib()
    # recovered_case = attr.ib()
    # death_case = attr.ib()

db_setup.create_tables()
scheduler = BackgroundScheduler()
corona_virus_data_process()
job = scheduler.add_job(corona_virus_data_process, 'interval', minutes=60)
scheduler.start()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
