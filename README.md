Upgrade pip
sudo pip3 install --upgrade pip

Install dependencies
sudo -H pip3 install -r requirements.txt

Start
FLASK_ENV=development flask run

To access heroku psql
heroku pg:psql

### Development Notes

- Start venv: `venv`
- Start flask: `flask run`
- Start postgres
- using curl: `curl http://127.0.0.1:5000/test`
- using browser: `localhost:5000`

### Testing
