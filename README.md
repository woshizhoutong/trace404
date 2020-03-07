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

#### Run Flask with
python3 main.py


docker run -p 3306:3306 --name mysql-test-3 -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:latest
mysql -h 127.0.0.1 -P 3306 -u root -p