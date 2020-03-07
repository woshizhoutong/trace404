# Flask project for monitoring CoronaVirus in USA.

### How to deploy to GCP?
1. Follow the tutorial in AppEngine.
2. Command for deployment: gcloud app deploy app.yaml --project ordinal-avatar-270006
3. There must be a main.py to start the Flask App.

I am also using GCP to auto manage the https ssl for my domain 404trace.com.

4. Stream log: gcloud app logs tail -s default

### How to run locally

#### Install python required packages with 
pip install -r requirements.txt

#### Set up local mysql DB using docker
Make sure you have Docker installed. You may find the download img from here https://docs.docker.com/install/.

docker run -p 3306:3306 --name db_test -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:latest

#### Access local mysql DB
mysql -h 127.0.0.1 -P 3306 -u root -p

create a database named "db_test" with command:

CREATE DATABASE db_test;


#### Run Flask with
uncomment the setting code for local db in db_setup.py.

python3 main.py
