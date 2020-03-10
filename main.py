#!/usr/bin/env python
import json
import os
import flask
import datetime

from models.models import News, CoronaVirusData
from service import news_api_util, db_service
from service import github_jhu_data
from apscheduler.schedulers.background import BackgroundScheduler
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = flask.Flask(__name__)

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
    news_content_list = db_service.retrieve_news_content_by_id(news_id)

    news_dict = {}
    if news_list and news_content_list:
        news = news_list[0]
        news_content = news_content_list[0]
        news_schema = NewsSchema()
        news_dict = news_schema.dump(news)
        news_dict['content'] = news_content.content

    return flask.render_template('post.html', news=news_dict)


@app.route("/news")
def get_news():
    query = flask.request.args.get('q')
    query_in_title = flask.request.args.get('query_in_title', '')
    print (query_in_title)
    from_date = datetime.datetime.now().strftime("%Y-%m-%d")
    to_date = datetime.datetime.now().strftime("%Y-%m-%d")

    news_list = news_api_util.read_from_news_api(query=query, from_date=from_date, to_date=to_date,
                                                 query_in_title=query_in_title)
    news_schema = NewsSchema()
    dump_news_list = [news_schema.dump(news) for news in news_list]
    return json.dumps(dump_news_list)


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


@app.route("/today_usa_data")
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
        # times 1000 to change the time to milliseconds
        'last_updated_at': last_updated_at * 1000
    }
    json_string = json.dumps(response)
    return json_string


def corona_virus_data_process():
    print('Loading daily report from github.')
    github_jhu_data.daily_data_process()
    # github_jhu_data.compute_data_delta()

scheduler = BackgroundScheduler()
corona_virus_data_process()
job = scheduler.add_job(corona_virus_data_process, 'interval', minutes=60)
scheduler.start()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
