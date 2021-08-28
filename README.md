Upgrade pip
sudo pip3 install --upgrade pip

Install dependencies
sudo -H pip3 install -r requirements.txt

Start
FLASK_ENV=development flask run

To access heroku psql
heroku pg:psql
