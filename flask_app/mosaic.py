#!/usr/local/bin/python
# -*- coding: utf-8  -*-


"""

Мозаика ТВ-каналов на ffmpeg

"""

from daemon import Daemon
from methods import *
from config import conf


def make(sid, name='Test1'):  # Скриншот канала под номером sid
    path = '%s/flask_app/static/mosaic/' % conf['APP_DIR']
    timestamp = datetime.now().strftime("%D %T")
    os.system(  # Захват ffmpeg'ом
        "ffmpeg -v quiet -ss 00:00:00 -i http://%s/%s -f mjpeg -vframes 1 -s 160x140 %s%s.jpg -y"
        % (conf['STREAM_SERVER'], sid, path, sid)
    )
    os.system(  # Подпись номера
        "convert %s%s.jpg -background Khaki label:'%s' -gravity Center -append %s%s.jpg"
        % (path, sid, timestamp, path, sid)
    )
    os.system(  # Подпись назвния
        "convert %s%s.jpg -background Khaki label:'%s' -gravity North -append %s%s.jpg"
        % (path, sid, ' '.join([str(sid), name.encode("utf8")]), path, sid)
    )


def mosaic_start(channels):  # Запуск для готового списка каналов
    while 1:
        for sid, channel in channels.iteritems():
            make(sid, channel.name)


class MyDaemon(Daemon):
    def run(self):  # Перегрузка метода run() для объекта класса Daemon
        db = db_init(conf)
        channels = channel_init(db)
        mosaic_start(channels)


if __name__ == "__main__":
    daemon = MyDaemon('/var/run/mosaic.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print "starting.."
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'Unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
