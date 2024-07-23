# Colibri node server

## Setup

Create a python virtual environment:
```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

And run the server to serve its API:
```sh
.venv/bin/fastapi run api.py --port 8000
```

Once the server is running, it will serve at [localhost:8000](http://localhost:8000). You can check its API documentation at `http://localhost:8000/docs`.

## Deployment

In order for other people to access and use the server, you only need the machine with the server to be accessible from the outside. This can be done by running Colibri on a server with a static ip address, or by using exposing Colibri as a Tor or I2P hidden service.

If you decide to host a Colibri node, please tell me so I can list them in the main page.

