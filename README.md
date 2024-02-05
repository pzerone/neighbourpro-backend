## NeighbourPro backend

## Development setup
project dependencies and virtual environments are managed using [python-poetry](https://python-poetry.org/docs/). Use the provided `requirements.txt` file if you would like to use pip instead.

**Note**: You must take care of virtual environment manually if you do not intent to use poetry.
* Install dependendencies and create virtual env using `poetry`
    
  ```bash
  poetry install --no-root
  ```
* Copy `env.sample` file to `.env` and modify variables
* Run:
  ```bash
  ./startup.sh dev
  ```

`startup.sh` will run the server in development mode with hot-reloading enabled.
## Deploy
* Ensure docker and docker compose are installed
* Copy `env.sample` to `.env` and make required changes
* Deploy using docker compose
    
  ```bash
  docker compose up -d --build --force-recreate
  ```

This will run the server in production mode without hot reloading.

`force-recreate` flag is optional, but allows for a clean deployment and is recommended.

**Note**: Docker script is setup to only use `requirments.txt` to install dependencies. This ensures that the image is free of un-needed dependencies. One must generate an updated `requirements.txt` using poetry if there are local changes.

To do that, run:

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```
