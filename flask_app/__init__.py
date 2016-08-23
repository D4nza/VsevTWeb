#!/usr/local/bin/python
# -*- coding: utf-8  -*-

from log import Log
from config import conf
from flask import Flask
import os, signal


app = Flask(__name__, static_url_path="", static_folder="static")
app.config.update(conf)

from methods import db_init, channel_init, signal_handler

db = db_init(app.config)
cursor = db.cursor()
channels = channel_init(db)
os.system("echo > %s" % app.config['LOG_FILE'])
astra_log = Log()

import flask_app.astra
import flask_app.billing_API
import flask_app.frontend
import flask_app.rrdgraph

signal.signal(signal.SIGINT, signal_handler)
