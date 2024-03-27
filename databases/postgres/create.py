import utils
from pathlib import Path

import datetime
import random

def getStringFromDate(date):
    return date.strftime("%Y-%m-%d")

def getStringFromDateTime(date):
    return date.strftime("%Y-%m-%d %H:%M")

# Создание базы данных
def createDatabase(psql, dbName):
    psql.execute(
        f"CREATE DATABASE {dbName}"
    )

# ------------------------------------------

# Создание таблицы групп
def createTableGroups(psql):
    return psql.execute(
        f"CREATE TABLE {utils.TABLE_GROUPS} 
        (id VARCHAR(12) PRIMARY KEY);"
    )

# Создание таблицы студентов
def createTableStudents(psql):
    return psql.execute(
        f"CREATE TABLE {utils.TABLE_STUDENTS} 
            (
                id VARCHAR(8) PRIMARY KEY, 
                name VARCHAR(20) NOT NULL, 
                surname VARCHAR(20) NOT NULL, 
                group_fk VARCHAR(12) NOT NULL, 
                    FOREIGN KEY (group_fk) 
                    REFERENCES {utils.TABLE_GROUPS} (id)
            );"
    )

# Создание таблицы занятий
def createTableLessons(psql):
    # Тип занятия (лекция, практика)
    psql.execute(
        f"CREATE TYPE lesson_type AS ENUM ('Практика', 'Лекция');"
    )

    return psql.execute(
        f"CREATE TABLE {utils.TABLE_LESSONS} 
            (
                id SERIAL PRIMARY KEY, 
                type lesson_type NOT NULL
            );"
    )

# Создание таблицы материалов занятий
def createTableLessonMaterials(psql):
    return psql.execute(
        f"CREATE TABLE {utils.TABLE_LESSON_MATERIALS} 
            (
                id SERIAL PRIMARY KEY, 
                lesson_fk INT REFERENCES {utils.TABLE_LESSONS} (id) NOT NULL, 
                title VARCHAR(50) NOT NULL, 
                description VARCHAR(255) NOT NULL
            )"
    )

# Создание таблицы расписания
def createTableSchedule(psql):
    return psql.execute(
        f"CREATE TABLE {utils.TABLE_SCHEDULE} 
            (
                id SERIAL, 
                group_fk VARCHAR(12) REFERENCES {utils.TABLE_GROUPS} (id) NOT NULL, 
                lesson_fk INT REFERENCES {utils.TABLE_LESSONS} (id) NOT NULL, 
                time TIMESTAMP NOT NULL
            ) 
                PARTITION BY RANGE (time);"
    )

# Создание таблицы с частью расписания с конкретным временным промежутком
def createTableSchedulePartition(psql, partitonName, timeFrom, timeTo):
    return psql.execute(
        f"CREATE TABLE {partitonName} 
            PARTITION OF {utils.TABLE_SCHEDULE} 
            FOR VALUES FROM ('{timeFrom}') TO ('{timeTo}');"
    )

# Создание таблицы посещений
def createTableVisits(psql):
    return psql.execute(
        f"CREATE TABLE {utils.TABLE_VISITS} 
            (
                id SERIAL PRIMARY KEY, 
                visited boolean NOT NULL, 
                student_fk VARCHAR(8) NOT NULL, 
                schedule_fk INT NOT NULL, 
                FOREIGN KEY (student_fk) REFERENCES {utils.TABLE_STUDENTS} (id)
            );"
    )


START_SEMESTER_WEEK = datetime.datetime(2023, 9, 1)
WEEK_DELTA = datetime.timedelta(weeks = 1)
DAY_DELTA = datetime.timedelta(days = 1)
WEEKS_TO_FILL = 32

STUDENTS = []

GROUPS = ['БСБО-01-20', 'БСБО-02-20', 'БСБО-03-20', 'БСБО-04-20', 'БСБО-05-20', 'БСБО-06-20', 'БСБО-07-20', 'БСБО-08-20', 'БСБО-09-20', 'БСБО-10-20', 'БСБО-11-20', 'БСБО-12-20', 'БСБО-13-20', 'БСБО-14-20', 'БСБО-15-20', 'БСБО-16-20', 'БСБО-17-20', 'БСБО-18-20']

LESSONS = ['Математика', "Программирование", "Философия", "Проектирование архитектуры ПО", "Информационная безопасность"]


def createScheme(postgre):

    createTableGroups(postgre)
    createTableStudents(postgre)
    createTableLessons(postgre)
    createTableLessonMaterials(postgre)
    createTableSchedule(postgre)

    currentWeek = START_SEMESTER_WEEK

    for week in range(1, WEEKS_TO_FILL + 1):
        partitionTableName = utils.TABLE_SCHEDULE + str(currentWeek.year) + "week" + str(week)
        weekEnd = currentWeek + WEEK_DELTA

        createTableSchedulePartition(postgre, partitionTableName, currentWeek.strftime("%Y-%m-%d"), weekEnd.strftime("%Y-%m-%d"))

        currentWeek = weekEnd

    createTableVisits(postgre)

def generateStudentId():
    russianLetters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЫЭЮЯ"
    nums = "1234567890"
    return "20" + "".join(random.choices(russianLetters, k=2)) + "".join(random.choices(nums, k=4))

def generateData():
    names = Path("data/names.txt").read_text().splitlines()
    surnames = Path("data/surnames.txt").read_text().splitlines()

    namesLen = len(names)
    surnamesLen = len(surnames)

    for group in GROUPS:
        for i in range(random.randint(20,30)):
            studentId = generateStudentId()
            student = {"id" : studentId, "name" : names[random.randint(0, namesLen-1)], "surname": surnames[random.randint(0, surnamesLen-1)], "group": group}
            STUDENTS.append(student)


def shouldAddGroup():
    return random.random() < 0.8

def shouldAdd(prob):
    return random.random() < prob

def insertGroup(psql, group):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_GROUPS} (id) 
            VALUES ('{group}');"
    )

def insertStudent(psql, studentId, studentName, studentSurname, group):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_STUDENTS} (id, name, surname, group_fk) 
            VALUES ('{studentId}', '{studentName}', '{studentSurname}', '{group}');"
    )

def insertLesson(psql, name, type, courseId):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_LESSONS} (description_fk, type, course_fk) 
            VALUES ('{name}', '{type}', '{courseId}');"
    )

def insertLessonMaterials(psql, lesson, title, description):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_LESSON_MATERIALS} (lesson_fk, title, description) 
            VALUES ('{lesson}', '{title}', '{description}');"
    )

def insertSchedule(psql, group, lesson, time):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_SCHEDULE} (group_fk, lesson_fk, time) 
            VALUES ('{group}', {lesson}, '{time}');"
    )

def insertVisit(psql, schedule_fk, student, visited):
    return psql.execute(
        f"INSERT INTO {utils.TABLE_VISITS} (schedule_fk, student_fk, visited) 
            VALUES ('{schedule_fk}', '{student}', {visited});"
    )

def fillDay(psql, day, group, lessons):
    lessonsTime = [datetime.timedelta(hours=9), datetime.timedelta(hours=10.5), datetime.timedelta(hours=12.5), datetime.timedelta(hours=14, minutes=20), datetime.timedelta(hours=16, minutes=20), datetime.timedelta(hours=18)]
    for lessonTime in lessonsTime:
        if not shouldAdd(0.4):
            continue

        lesson = random.choice(lessons)

        insertSchedule(psql, group, lesson["id"], day + lessonTime)

def fillWeek(psql, week, group, lessons):
    currentDay = week

    for i in range(6):
        fillDay(psql, currentDay, group, lessons)
        currentDay += DAY_DELTA

def fillSchedule(psql, group, lessons):
    currentWeek = START_SEMESTER_WEEK

    for i in range(WEEKS_TO_FILL):
        lesson = random.choices(lessons, k=5)
        #lessons = random.choices(range(1, len(LESSONS)+1), k=3)
        fillWeek(psql, currentWeek, group, lesson)

        currentWeek += WEEK_DELTA

def fillVisits(psql, schedl):
    for student in filter(lambda student: student["group"] == schedl["group_fk"], STUDENTS):
        insertVisit(psql, schedl["id"], student["id"], shouldAdd(0.8))


def fillScheme(postgre, specialitites = '', courses = '', lessons_descriptions = '', lesson_materials = ''):
    generateData()

    for group in GROUPS:
        insertGroup(postgre, group, random.choice(specialitites))

    for student in STUDENTS:
        insertStudent(postgre, student["id"], student["name"], student["surname"], student["group"])

    for lesson in lessons_descriptions:
        insertLesson(postgre, lesson, "Лекция" if shouldAdd(0.5) else "Практика", random.choice(courses))

    for lesson_material in lesson_materials:
        insertLessonMaterials(postgre, )

    lessons = utils.getLessons(postgre)
    
    #Filling schedule
    for group in GROUPS:
        if not shouldAdd(0.3):
            continue    

        fillSchedule(postgre, group, lessons)

    #Filling visits
    schedule = utils.getSchedule(postgre)
    for mg in schedule:
        fillVisits(postgre, mg)