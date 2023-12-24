## NeighbourPro backend

## Development setup
> project dependencies and virtual environments are managed using pipenv. Use the provided `requirements.txt` file if you would like to use pip instead and manually create virtual environment.
* Install dependendencies and create virtual env using `pipenv`
    
    ```pipenv install```
* Copy `env.sample` file to `.env` and modify variables
* Run ```./startup.sh```
> `startup.sh` will run the server in development mode with hot-reloading enabled.
## Deploy
* Ensure docker and docker compose are installed
* Copy `env.sample` to `.env` and make required changes
* disable hot-reloading by removing the `--reload` flag in `startup.sh` file
* Deploy using docker compose
    
    ```docker compose up -d --build --force-recreate```

> `force-recreate` flag is optional, but allows for a clean deployment and is recommended