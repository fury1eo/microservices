import os
from flask import Flask, request
import utils
import create
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import logging
import datetime
import requests
import json
import time
from urllib.parse import urlparse, parse_qs, unquote

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

postgre = None
elastic = None


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
            lections = tuple(utils.commaSeparatedParamsToList(lections[0]))

        start_date = datetime.datetime.strptime(args.get("from"), "%d-%m-%Y")
        end_date = datetime.datetime.strptime(args.get("until"), "%d-%m-%Y")

        app.logger.info(f"lessons = {lections}")
        app.logger.info(f"from = {start_date}")
        app.logger.info(f"until = {end_date}")

        return utils.findWorstStudents(postgre, lections, start_date, end_date)

    return getStudents(postgre)


@app.route("/api/groups", methods=["GET"])
def getGroups():
    return getGroups(postgre)


@app.route("/api/lessons", methods=["GET"])
def getLessons():
    return getLessons(postgre)


@app.route("/api/schedule", methods=["GET"])
def getSchedule():
    return getSchedule(postgre)


@app.route("/api/lesson_materials", methods=["GET", "POST"])
def getLessonMaterials():
    keyword = request.args.get('find', type = str)

    print(keyword)

    finalData = []
    
    if not keyword:
        app.logger.info(f"keyword = {keyword}")
        body = {'query':{"match_all": {}}}
        res= elastic.search(index='lesson_descriptions', filter_path=['hits.hits._source'], body=json.dumps(body))
        all_hits = res['hits']['hits']
        for num, doc in enumerate(all_hits):
            for value in doc.values():
                finalData.append(value)
        app.logger.info(finalData)
        return finalData
    
    print(finalData)

    body = {
        "query": {
        "multi_match" : {
            "query":  unquote(keyword),
            "fields": [ "equipment", "materials", "name" ]
        }
    }}
    app.logger.info(json.dumps(body, ensure_ascii=False))
    
    res = elastic.search(index="lesson_descriptions", filter_path=['hits.hits._source'], body=json.dumps(body, ensure_ascii=False))

    finalData = []
    all_hits = res['hits']['hits']

    app.logger.info(all_hits)

    for num, doc in enumerate(all_hits):
        for value in doc.values():
            finalData.append(value)

    app.logger.info(finalData)

    return finalData


    # res = elastic.search(index="lesson_descriptions", body={"query": {"match": {"content": "fox"}}})
    # print("%d documents found" % res['hits']['total'])
    # for doc in res['hits']['hits']:
    #     print("%s) %s" % (doc['_id'], doc['_source']['content']))


rows = [
    {
        "name": "Математика",
        "equipment": "учебники",
        "materials": "Область знаний, включающая изучение таких тем, как числа (арифметика и теория чисел), формулы и связанные с ними структуры (алгебра), формы и пространства, в которых они содержатся (геометрия), величины и их изменения (исчисление и анализ).",
    },
    {
        "name": "Русский язык",
        "equipment": "учебник",
        "materials": "Язык восточнославянской группы славянской ветви индоевропейской языковой семьи, национальный язык русского народа.",
    },
    {
        "name": "Английский язык",
        "equipment": "учебник",
        "materials": "Язык англо-фризской подгруппы западной группы германской ветви индоевропейской языковой семьи.",
    },
    {
        "name": "История",
        "equipment": "учебник",
        "materials": "Наука, исследующая прошлое, реальные факты и закономерности смены исторических событий, эволюцию общества и отношений внутри него.",
    },
    {
        "name": "Информатика",
        "equipment": "компьютер",
        "materials": "Наука о методах и процессах сбора, хранения, обработки, передачи, анализа и оценки информации с применением компьютерных технологий, обеспечивающих возможность её использования для принятия решений. ",
    },{
        "name": "Сети",
        "equipment": "провода",
        "materials": "Система, обеспечивающая обмен данными между вычислительными устройствами - компьютерами, серверами, маршрутизаторами.",
    },
    {
        "name": "Труд",
        "equipment": "табуретка",
        "materials": "Деятельность человека, направленная на создание материальных и духовных благ, которые удовлетворяют потребности индивида и общества.",
    },
    {
        "name": "Физкультура",
        "equipment": "Носки",
        "materials": "Область социальной деятельности, направленная на сохранение и укрепление здоровья человека в процессе осознанной двигательной активности.",
    },
    {
        "name": "Научная деятельность",
        "equipment": "Микроскоп",
        "materials": "Cовокупность целесообразных, предметно-направленных действий исследователя или группы исследователей по выработке, получению и теоретической систематизации объективных знаний о действительности.",
    },
]

mappings = {
        "properties": {
            "name": {"type": "text", "analyzer": "standard"},
            "equipment": {"type": "text", "analyzer": "standard"},
            "materials": {"type": "text", "analyzer": "standard"},
    }
}

#elastic.delete_by_query(index="lesson_descriptions", body={"query": {"match_all": {}}})
def createElasticTableLessonMaterials():
    elastic.indices.create(index="lesson_materials", mappings=mappings)

    for i, row in enumerate(rows):
        doc = {
            "name": row["name"],
            "equipment": row["equipment"],
            "materials": row["materials"],
        }

        elastic.index(index="lesson_materials", id=i, document=doc)


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
    response = tryToFetch("http://elastic:9200/api/lesson_materials")
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

    lessons_materials = getLessonsFromElastic()
    app.logger.info(lessons_materials)

    app.logger.info("Creating scheme")
    create.createScheme(postgre)
    app.logger.info("Created scheme")

    app.logger.info("Filling database")
    create.fillScheme(postgre, lessons_materials)
    app.logger.info("Filled database")

if __name__ == "__main__":
    app.logger.info("Connecting to postgres")
    postgre = utils.getPostgre()
    app.logger.info("Connected to postgres")

    if isSchemeCreated(postgre):
        app.logger.info("Scheme already created. Simple start")
    else:
        prepareDatabase(postgre)

    time.sleep(15)

    app.logger.info("Connecting to elastic")

    elastic = Elasticsearch("http://elastic:9200")
    app.logger.info("Connected to elastic")

    createElasticTableLessonMaterials()

    app.run(host="0.0.0.0", port=os.environ["LOCAL_SERVICES_PORT"])