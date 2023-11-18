## NeighbourPro backend

## Deploy
* Ensure docker and docker compose are installed
* copy `env.sample` to `.env` and make required changes

        docker compose up -d --build --force-recreate

`force-recreate` flag is optional, but allows for a clean deployment and is recommended