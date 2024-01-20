#!venv/Scripts/python
import os

from waitress import serve

from app import create_app

app = create_app()
HOST = '127.0.0.1'
PORT = int(os.getenv('HTTP_PORT') or 55000)
# app.run(host=HOST, port=PORT, debug=True, ssl_context=None)
serve(app, host=HOST, port=PORT)
