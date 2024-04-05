import os
from flask import Flask, request
import utils
import create
import logging
import datetime
import requests
import json
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

postgre = None


def isSchemeCreated(postgre):
    postgre.execute("SELECT * FROM information_schema.tables WHERE table_name = 'groups';")
    records = postgre.fetchall()

    if records:
        return True
    else:
        return False


def tryToFetch(url):
    while True:
        app.logger.info(f"Fetching {url} ...")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                app.logger.info(f"Fetching {url} successded!")
                return response
        except Exception:
            app.logger.info(f"Fetching {url} failed")
        time.sleep(0.5)


def getLessonsFromElastic():
    response = tryToFetch("http://elastic-ma:22808/api/lessons")
    lessons = response.json()

    app.logger.info(f"108) {lessons}")
    res = []
    for lesson in lessons:
        if isinstance(lesson, dict):
            res.append(lesson["name"])

    return res


def prepareDatabase(postgre):
    getLessonsFromElastic()

    time.sleep(1)

    lessons = getLessonsFromElastic()
    app.logger.info(lessons)

    app.logger.info("Creating scheme")
    create.createScheme(postgre)
    app.logger.info("Created scheme")

    app.logger.info("Filling database")
    # create.fillScheme(postgre, specs, courses, lessons)
    create.fillScheme(postgre, lessons)
    app.logger.info("Filled database")

if __name__ == "__main__":
    app.logger.info("Connecting to postgres")
    postgre = utils.getPostgre()
    app.logger.info("Connected to postgres")

    if isSchemeCreated(postgre):
        app.logger.info("Scheme already created. Simple start")
    else:
        prepareDatabase(postgre)

    app.run(host="0.0.0.0", port=os.environ["LOCAL_SERVICES_PORT"])