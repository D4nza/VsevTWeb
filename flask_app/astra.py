#!/usr/local/bin/python
# -*- coding: utf-8  -*-

"""

Модуль для обработки данных мониторинга Astra

Функционал:
1. Прием данных в формате JSON
2. Обновление параметров канала
3. Запись в лог в случае изменений

"""

from flask_app import *


@app.route('/astra_monitor/', methods=['POST'])
def astra_monit():
    #Парсинг данных
    content = request.get_json(silent=True)
    data = content[0]
    for sid, channel in channels.iteritems():
        #Обновление канала в случае его рестарта на астре
        if "channel" in data.keys():
            if sid == int(data["channel"]["id"]):
                astra_log.event(channel, data, "init")
                channel.__init__(sid, db, cursor)
        else:
            if str(sid) == str(data["channel_id"]):
                if data["onair"] == True:
                    #Обновление битрейта
                    channel.bitrate = data["bitrate"]
                    if data["cc_error"] > 0:
                        #Счетчик CC-ошибок
                        channel.cc += data["cc_error"]
                        astra_log.event(channel, data, "cc")
                    if data["pes_error"] > 0:
                        #Счетчик PES-ошибок
                        channel.pes += data["pes_error"]
                        astra_log.event(channel, data, "pes")
                    if int(data["input_id"]) != channel.input_id:
                        #Смена источника
                        channel.input_id = int(data["input_id"])
                        astra_log.event(channel, data, "switch")
    return '1'
