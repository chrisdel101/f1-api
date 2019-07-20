### Flask F1 api

##### To start

- Make sure python3 is installed
- create virtual env

```
python3.7 -m venv venv
. venv/bin/activate
```

- clone repo

```
git clone git@github.com:chrisdel101/f1-ap1.git
cd f1-api
```

- install dependencies

```
pip install --upgrade -r requirements.txt
```

- create ENV variables

```
touch .env
echo FLASK_ENV=development > .env
echo FLASK_APP=app.py >> .env
```

- start

```
flask run
localhost:5000 #optional
```
