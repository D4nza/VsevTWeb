#!/usr/local/bin/python
# -*- coding: utf-8  -*-


class Channel():
    def __init__(self, sid, db, cursor):
        db.commit()
        cursor.execute("SELECT * FROM `config` WHERE `id`=%s;" % sid)
        data = cursor.fetchall()[0]
        self.ts_id = data[0]
        self.name = data[2]
        self.sid = sid
        self.input_id = 1   # Порядковый номер источника, при запуске всегда 1
        self.bitrate = 0
        self.log = ''
        self.scrambled = 0
        self.cc = 0
        self.pes = 0
        self.primary = data[3]  # Основной источник
        self.secondary = data[4]   # Резерв
        self.codec = data[5]    # Кодировка
        self.analog = data[6]   # Порядковый номер в аналоговой сетке(если есть)
        self.oscam = data[7]    # Порядковый номер oscam-конфига(если есть)
        db.commit()
