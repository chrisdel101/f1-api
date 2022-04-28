#!/usr/local/bin/bash

heroku local -f Procfile.test -e .env.test --port 5001
