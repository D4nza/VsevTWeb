#!/usr/local/bin/python
# -*- coding: utf-8  -*-

"""

Полезные методы для инициализации приложения и прочего

"""

from channel import Channel
from datetime import datetime
from flask import request
from config import conf
import MySQLdb, sys, os


def shutdown_server():
    os.system('python %s/flask_app/rrdgraph.py stop' % conf['APP_DIR'])
    os.system('python %s/flask_app/mosaic.py stop' % conf['APP_DIR'])
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    os.system('python %s/flask_app/rrdgraph.py stop' % conf['APP_DIR'])
    os.system('python %s/flask_app/mosaic.py stop' % conf['APP_DIR'])
    sys.exit(0)


def logging(message):  # Лог для отлова багов приложения
    os.system("echo '%s: %s' >> %s/flask_app/log" %
              (str(datetime.now()),str(message),conf['APP_DIR']))


def db_init(config): # Инициализация БД
    db = MySQLdb.connect(
        host = config['DB_HOST'],
        user = config['DB_USER'],
        passwd = config['DB_PASSWD'],
        db = config['DB_NAME'],
        charset='utf8'
    )
    return db


def channel_init(db):  # Инициализация списка каналов
    cursor = db.cursor()
    channels = {}
    cursor.execute("SELECT `id` FROM `config`;")
    data = cursor.fetchall()
    for row in data:
        channels[row[0]] = Channel(row[0], db, cursor)
    return channels


def is_run(daemon_name):  # Проверка статуса демона
    return os.path.isfile("/var/run/%s.pid" % daemon_name)

    

