import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from config import Configuration

from tasks.data_scraper import Scraper



app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)


@app.route('/')
def index():
    return {}




if __name__ == '__main__':
    app.run()