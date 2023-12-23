#!/bin/sh
# migration files are inside the app/database folder
cd app/database

# apply database migrations using Aerich
aerich upgrade

cd ..
# Start the Uvicorn server with the FastAPI app. hot reload is for development only
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info