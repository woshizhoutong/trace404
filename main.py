#!/usr/bin/env python
import json
import logging
import os
import sys

import flask
import datetime

from flask_cors import CORS

from models.models import News, CoronaVirusData
from service import news_api_util, db_service
from service import github_jhu_data
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = flask.Flask(__name__)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

cors = CORS(app, resources={r"/api/*": {"origins": "example.com"}})

@app.route("/")
def index():
    return flask.render_template('index.html')


@app.route("/coronavirus")
def coronavirus():
    return flask.render_template('index.html')


@app.route("/news_page")
def news_page():
    news_id = flask.request.args.get('id')
    news_list = db_service.retrieve_news_by_id(news_id)

    news_dict = {}
    if news_list:
        news = news_list[0]
        news_schema = NewsSchema()
        news_dict = news_schema.dump(news)

    return flask.render_template('post.html', news=news_dict)


@app.route("/api/news")
def get_news():
    state = flask.request.args.get('state', 'US')

    news_list = news_api_util.read_all_serving_news(state)
    news_schema = NewsSchema()
    dump_news_list = [news_schema.dump(news) for news in news_list]
    return json.dumps(dump_news_list)


@app.route("/api/hourly_data_refresh")
def hourly_update():
    # According to GCP doc https://cloud.google.com/appengine/docs/flexible/nodejs/scheduling-jobs-with-cron-yaml
    # the cron job requests are always sent from "10.0.0.1"
    if flask.request.headers.get('X-Appengine-Cron'):
        app.logger.info("Loading daily report from github.")
        github_jhu_data.daily_data_process()
        news_api_util.update_news('coronavirus', 'US')
        return "Done"
    app.logger.info("Access to /hourly_data_refresh from non-cron job is rejected.")
    return "Not Authorized"



class DataItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CoronaVirusData
        include_fk = True
        load_instance = True


class NewsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = News
        include_fk = True
        load_instance = True


@app.route("/api/today_usa_data")
def get_today_usa_data():
    data_list, last_updated_at = github_jhu_data.read_usa_daily_report()
    sum_of_confirmed = 0
    sum_of_death = 0
    sum_of_recovered = 0

    data_item_schema = DataItemSchema()
    dump_corona_virus_data_item_list = [data_item_schema.dump(data) for data in data_list]
    for data in data_list:
        sum_of_confirmed += data.confirmed_case
        sum_of_death += data.death_case
        sum_of_recovered += data.recovered_case

    confirmed_case_delta = 0
    death_case_delta = 0
    recovered_case_delta = 0
    delta_data_list = github_jhu_data.compute_data_delta()
    for data in delta_data_list:
        confirmed_case_delta += data.confirmed_case
        death_case_delta += data.death_case
        recovered_case_delta += data.recovered_case

    response = {
        'sum_of_confirmed': sum_of_confirmed,
        'sum_of_death': sum_of_death,
        'sum_of_recovered': sum_of_recovered,
        'data': dump_corona_virus_data_item_list,
        'sum_of_confirmed_case_delta': confirmed_case_delta,
        'sum_of_death_case_delta': death_case_delta,
        'sum_of_recovered_case_delta': recovered_case_delta,
        # give last_updated_at as string
        'last_updated_at': last_updated_at.strftime('%m/%d/%Y')
    }
    json_string = json.dumps(response)
    return json_string


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
