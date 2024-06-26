import os
import psycopg2
import time

TABLE_STUDENTS = "students"
TABLE_GROUPS = "groups"
TABLE_VISITS = "visits"
TABLE_LESSONS = "lessons"
TABLE_LESSON_MATERIALS = "lesson_materials"
TABLE_SCHEDULE = "schedule"


def tryToСonnect():
    try:
        return psycopg2.connect(dbname=os.environ["POSTGRE_DBNAME"], user=os.environ["POSTGRE_USER"], 
                        password=os.environ["POSTGRE_PASS"], host="postgres", connect_timeout=30)
    except Exception:
        return None


def getPostgre():
    for trying in range(10):
        conn = tryToСonnect()

        if conn is not None:
            break

        time.sleep(0.5)
        
    conn.autocommit = True
    return conn.cursor()


def getStudents(postgre):
    postgre.execute(
        "SELECT * FROM students"
    )
    students = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return students


def getGroups(postgre):
    postgre.execute(
        "SELECT * FROM groups"
    )
    groups = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return groups


def getSchedule(postgre):
    postgre.execute(
        "SELECT * FROM schedule"
    )
    schedule = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return schedule


def getLessons(postgre):
    postgre.execute(
        "SELECT * FROM lessons"
    )
    lessons = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return lessons


def getCourses(postgre):
    postgre.execute("""
        SELECT group_fk, course_fk 
        FROM schedule 
        JOIN lessons ON schedule.lesson_fk = lessons.id 
        GROUP BY group_fk, course_fk;
    """)
    courses = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
    return courses


def findWorstStudents(postgre, lections, start_date, end_date):
  postgre.execute(f"SELECT student_fk AS id, CAST(COUNT(CASE visited WHEN true THEN 1 ELSE NULL END) AS FLOAT) / COUNT(*) AS visit_percent \
    FROM visits JOIN schedule ON visits.schedule_fk = schedule.id \
    WHERE schedule.lesson_fk IN {lections} AND schedule.time BETWEEN '{start_date}' AND '{end_date}' \
    GROUP BY student_fk \
    ORDER BY visit_percent \
    LIMIT 10;")

  students = [dict((postgre.description[i][0], value) for i, value in enumerate(row)) for row in postgre.fetchall()]
  return students


def commaSeparatedParamsToList(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val)
    return result