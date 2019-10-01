#!/bin/bash
FLASK_ENV=prod_testing LOGS=off python -m unittest test_app
echo $?
# curl https://f1-api.herokuapp.com/teams/scrape-teams
# curl https://f1-api.herokuapp.com/drivers/scrape-drivers