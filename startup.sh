#!/bin/bash

set -e

# Check if a command line argument is provided
if [ $# -eq 0 ]; then
    echo -e "\e[91mError: Please provide a command line argument ('dev' or 'prod')\e[0m" >&2
    exit 1
fi

# delay for 5 seconds to allow the database to start up in production.
# This is a temporary fix to allow the database to start up before the migration is run
# This should be replaced with health check of docker without exposing database credentials on the compose file
if [ "$1" == "prod" ]; then
    sleep 5
fi

# Apply database migrations using Aerich
# Returns early with failure if db connection fails
echo -e "\e[92mApplying database migrations:\e[0m aerich upgrade"
if ! aerich upgrade > /dev/null 2>&1; then
    echo -e "\e[91mError: Database migration failed. Check if the database is up and running\e[0m" >&2
    exit 1
fi

# Determine whether to use --reload based on the command line argument
if [ "$1" == "dev" ]; then
    echo -e "\e[92mRunning uvicorn server in dev mode:\e[0m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info"
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info
elif [ "$1" == "prod" ]; then
    echo -e "\e[92mRunning uvicorn server in production mode:\e[0m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
else
    echo -e "\e[91mError: Unknown parameter. Please use 'dev' or 'prod'\e[0m" >&2
    exit 1
fi
