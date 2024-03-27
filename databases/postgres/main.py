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


def commaSeparatedParamsToList(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val)
    return result


@app.route('/api/echo', methods=['GET'])
def echo():
    return 'Hello Postgres!'


@app.route("/api/students", methods=["GET"])
def getStudents():
    args = request.args

    if "from" in args and "until" in args and "lessons" in args:
        app.logger.info("Search request")

        lections = args.getlist("lessons")
        if len(lections) == 1 and ',' in lections[0]:
            lections = tuple(commaSeparatedParamsToList(lections[0]))

        start_date = datetime.datetime.strptime(args.get("from"), "%d-%m-%Y")
        end_date = datetime.datetime.strptime(args.get("until"), "%d-%m-%Y")

        app.logger.info(f"lessons = {lections}")
        app.logger.info(f"from = {start_date}")
        app.logger.info(f"until = {end_date}")

        return utils.findWorstStudents(postgre, lections, start_date, end_date)

    return utils.getStudents(postgre)


@app.route("/api/groups", methods=["GET"])
def getGroups():
    return utils.getGroups(postgre)


@app.route("/api/lessons", methods=["GET"])
def getLessons():
    return utils.getLessons(postgre)


@app.route("/api/courses", methods=["GET"])
def getCourses():
    groupsToCourses = utils.getCourses(postgre)
    mappedGroups = dict()

    for groupToCourse in groupsToCourses:
        group = groupToCourse["group_fk"]
        course = groupToCourse["course_fk"]

        if course not in mappedGroups:
            mappedGroups[course] = []

        mappedGroups[course].append(group)

    res = []

    for key, val in mappedGroups.items():
        res.append({"name": key, "groups": val})

    return res


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


# def getCoursesFromMongo():
#     response = tryToFetch("http://mongo-ma:22808/api/courses")
#     insts = response.json()

#     courses = []
#     for deps in insts:
#         for dep in deps["department"]:
#             for course in dep["courses"]:
#                 name = course["name"]
#                 courses.append(name)
                   
#     return courses


# def getSpecialitiesFromMongo():
#     response = tryToFetch("http://mongo-ma:22808/api/specialities")
#     insts = response.json()

#     specs = []
#     for deps in insts:
#         for dep in deps["department"]:
#             for spec in dep["specs"]:
#                 name = spec["name"]
#                 specs.append(name)

#     return specs


# def getLessonsFromElastic():
#     response = tryToFetch("http://elastic-ma:22808/api/lessons")
#     lessons = response.json()

#     app.logger.info(f"108) {lessons}")
#     res = []
#     for lesson in lessons:
#         if isinstance(lesson, dict):
#             res.append(lesson["name"])

#     return res


def prepareDatabase(postgre):
    # courses = getCoursesFromMongo()

    # specs = getSpecialitiesFromMongo()

    # getLessonsFromElastic()

    time.sleep(1)

    # lessons = getLessonsFromElastic()
    # app.logger.info(lessons)

    app.logger.info("Creating scheme")
    create.createScheme(postgre)
    app.logger.info("Created scheme")

    app.logger.info("Filling database")
    # create.fillScheme(postgre, specs, courses, lessons)
    create.fillScheme(postgre)
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