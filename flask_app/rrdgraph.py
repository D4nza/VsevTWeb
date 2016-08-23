#!/usr/local/bin/python
# -*- coding: utf-8  -*-

"""

Рисовалка графиков на rrdtool

"""

from daemon import Daemon
import time, rrdtool, sys
from methods import *
from config import conf

db_dir = conf['APP_DIR'] + "/flask_app/static/rrddbs/"
pic_dir = conf['APP_DIR'] + "/flask_app/static/graph/"


def rrd_create(sid, step):  # Инициализация БД
    fname = db_dir + "channel%s.rrd" % sid
    if not os.path.isfile(fname):
        print "Creating database.."
        rrdtool.create(
            fname,
            "--step", str(step),
            "DS:bitrate:GAUGE:%s:0:100" % str(2 * step),
            "RRA:AVERAGE:0.5:1:576",
            "RRA:AVERAGE:0.5:6:672",
            "RRA:AVERAGE:0.5:24:732"
        )
        print fname
    else:
        print "Database already exist"


def rrd_update(sid, value):  # Обновление БД
    fname = db_dir + "/channel%s.rrd" % sid
    rrdtool.update(fname, "N:%s" % str(value))


def make_graph(sid, period, name):  # Отрисовка графика
    fname = db_dir + "/channel%s.rrd" % sid
    rrdtool.graph(pic_dir + "%s/%s.png" % (period, sid),
                  "--imgformat", "PNG",
                  "--height", "100",
                  "--width", "450",
                  "--end", "now",
                  "--start", "end-1%s" % period[0],
                  "--lower-limit", "0.0",
                  "--upper-limit", "10.0",
                  "--zoom", "1.2",
                  "--vertical-label=Mbps",
                  "--title", "Канал %s(%s) - %s" % (sid, name.encode("utf8"), period),
                  "DEF:avl=%s:bitrate:AVERAGE" % fname,
                  "AREA:avl#00FF00:Bitrate(mbps)",
                  'GPRINT:avl:AVERAGE:avg\: %2.2lf%%')


def get_bitrate(port):  # Функция значения
    string = os.popen(  # SNMP-запрос на получение битрейта
        "snmpwalk -c public -v 1 109.230.128.140 1.3.6.1.4.1.32285.2.2.1.4022.200.1.6.7.1.%s" % port).read()
    value = string.split('"')[1][:-3]
    if value[-1] == 'M':
        return float(value[:-1])
    elif value[-1] == 'K':
        return float(value[:-1]) / 1024
    else:
        return (float(value) / 1024) / 1024


def init_dbs(channels):  # Инициализация для всех каналов из списка
    for i, channel in channels.iteritems():
        rrd_create(i, 30)
        print "database created for channel %s(%s)" % (i, channel.name)


def rrdstart(channels):  # Запуск мониторинга
    while (1):
        for i, channel in channels.iteritems():
            bitrate = get_bitrate(i)
            rrd_update(i, str(bitrate))
            print "%s, %s: %s" % (i, channel.name, bitrate)
            make_graph(i, 'hour', channel.name)
            make_graph(i, 'day', channel.name)
            make_graph(i, 'week', channel.name)
        time.sleep(10)


class MyDaemon(Daemon):
    def run(self):  # Перегрузка метода run() для объекта класса Daemon
        db = db_init(conf)
        channels = channel_init(db)
        rrdstart(channels)


if __name__ == "__main__":
    daemon = MyDaemon('/var/run/rrdgraph.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'init':
            os.system("rm -f %s/*.rrd" % db_dir)
            db = db_init(conf)
            channels = channel_init(db)
            init_dbs(channels)
        else:
            print 'Unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|init" % sys.argv[0]
        sys.exit(2)
