#!/usr/local/bin/python
# -*- coding: utf-8  -*-

"""

Маршрутизация URL для Веб-интерфейса

"""

from flask import render_template
from flask_httpauth import HTTPBasicAuth
from flask_app import *
from methods import *

auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    users = app.config['HTTP_AUTH']
    if username in users:
        return users.get(username)
    return None


@app.route('/monitor/index/')
@auth.login_required
def index():
    return render_template(
        'index.html',
        channels=channels
    )


@app.route('/monitor/mosaic/')
@app.route('/monitor/mosaic/<command>')
@auth.login_required
def mosaic_daemon(command=None):
    if command:
        os.system('python %s/flask_app/mosaic.py %s' % (app.config['APP_DIR'], command))
    last_upd = os.popen(
        "ls -t -1 %s/flask_app/static/mosaic | head -1 | sed -e 's/\..*$//'" % app.config['APP_DIR']
    ).read()
    return render_template(
        'mosaic.html',
        channels=channels,
        is_run=is_run('mosaic'),
        last_upd=int(last_upd)
    )


@app.route('/monitor/graph/')
@app.route('/monitor/graph/<command>')
@auth.login_required
def graph_daemon(command=None):
    if command:
        os.system('python %s/flask_app/rrdgraph.py %s' % (app.config['APP_DIR'], command))
    return render_template(
        'graph.html',
        channels=channels,
        is_run=is_run('rrdgraph')


@app.route('/monitor/adapter/')
@auth.login_required
def adapter():
    return render_template('adapter.html')


@app.route('/monitor/log/')
@auth.login_required
def log():
    return render_template(
        'log.html',
        channels=channels,
        events=astra_log.Events
    )


@app.route('/monitor/channel/<int:sid>')
@auth.login_required
def channel(sid):
    return render_template(
        'channel.html',
        src="http://%s/%s" % (app.config['STREAM_SERVER'], sid),
        events=astra_log.selection(sid),
        channel=channels[sid]
    )


@app.route('/monitor/restart_analog/<int:number>')
@auth.login_required
def restart_analog(number):
    res = os.popen('ssh root@%s "python /root/work/usb_test.py %s"' %
                   (app.config['DVB_SERVER'], number))
    answer = res.read().split("\n")[0]
    return render_template(
        'reboot.html',
        answer=str(answer)
    )


@app.route('/monitor/restart_oscam/<int:number>')
@auth.login_required
def restart_oscam(number):
    os.popen('ssh root@%s "bash /root/work/oscam.sh %s"' %
             (app.config['DVB_SERVER'], number))
    answer = 'Done!'
    return render_template(
        'reboot.html',
        answer=str(answer)
    )


@app.route('/monitor/shutdown/')
@auth.login_required
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
