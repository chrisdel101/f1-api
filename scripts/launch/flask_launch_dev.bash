#!/usr/local/bin/bash
FLASK_ENV=dev_testing LOGS=off python -m unittest test_app
if [[ $? == 0 ]]; then
    echo 'TEST OKAY: RUN SCRAPER'
    curl localhost:5000/scrape-all
fi