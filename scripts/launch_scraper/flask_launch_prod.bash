#!/bin/bash
# run tests
FLASK_ENV=prod_testing LOGS=off python -m unittest test_app
# if tests pass run scraper
if [[ $? == 0 ]]; then
    echo 'TEST OKAY: RUN SCRAPER'
    curl https://f1-api.herokuapp.com/teams/scrape-teams
    curl https://f1-api.herokuapp.com/drivers/scrape-drivers
else
    echo "TESTS FAILED"
fi

if [[ $? == 0 ]]; then
    echo 'Success'
else
    echo 'Failure'
fi