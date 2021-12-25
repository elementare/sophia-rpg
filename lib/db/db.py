import os
from os.path import isfile
from sqlite3 import connect

from apscheduler.triggers.cron import CronTrigger

DB_PATH = "./data/db/database.db"
BUILD_PATH = "./data/db/build.sql"

cxn = connect(DB_PATH, check_same_thread=False, timeout=20) #Conexão com o banco de dados
cxn.execute("PRAGMA journal_mode=WAL") #Executar o banco de dados de modo que se possa ler e escrever ao mesmo tempo
cur = cxn.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)


def commit():
    cxn.commit()


def mexec(command, values):
    cur.execute(command, values)

def autosave(sched):
    sched.add_job(commit, CronTrigger(second=0))

def check_commit():
    return cur.rowcount

def close():
    cur.close()
    cxn.close()
    print('Fechei a conexão')

def connect():
    try:
        cxn = connect(DB_PATH, check_same_thread=False, timeout=10)
        cxn.execute("PRAGMA journal_mode=WAL")
        cur = cxn.cursor()
    except:
        print('Não consegui me conectar')


def field(command, *values):
    cur.execute(command, tuple(values))

    if (fetch := cur.fetchone()) is not None:
        return fetch[0]


def record(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchone()


def records(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchall()


def column(command, *values):
    cur.execute(command, tuple(values))

    return [item[0] for item in cur.fetchall()]


def execute(command, *values):
    cur.execute(command, tuple(values))


def multiexec(command, valueset):
    """

    :rtype:
    """
    cur.executemany(command, valueset)


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cur.executescript(script.read())
