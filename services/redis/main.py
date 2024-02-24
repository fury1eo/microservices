import os
from unittest import mock
from urllib import response
from flask import Flask, jsonify, request
import logging
import utils
# import redis_create as filler
import json

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as fp:
        file = json.load(fp)
        return file

redis = None

@app.route("/api/echo", methods=["GET"])
def echo():
    return "Hello Redis!"

@app.route("/api/all", methods=["GET"])
def get_all():
    res = utils.get_all(redis)
    return res

if __name__ == "__main__":
    # app.logger.info("Connecting to redis")
    # redis = utils.get_redis()
    # redis.drop_database("mirea-db")
    # app.logger.info("Connected to redis")

    # app.logger.info("Filling redis")
    # redis = redis["mirea-db"]["institutes"]

    # app.logger.info("Filled redis")

    #utils.get_institute(redis, "Институт кибербезопасности и цифровых технологий")

    app.run(host="0.0.0.0", port=os.environ["LOCAL_SERVICES_PORT"])