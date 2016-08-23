#!/usr/local/bin/python
# -*- coding: utf-8  -*-

"""

Модуль для обработки запросов биллинг-системы

1. Принимает JSON-объект.
2. Выполняет одну из 7 функций в зависимости от кода комманды.
3. Возвращает ответный код.

"""


from datetime import datetime
from flask_app import *
from flask import request


@app.route('/api/', methods=['GET'])
def api():
    args = request.args
    if not (args.get('api-key')) or not (args.get('command')):
        return '1'
    else:
        if not (args.get('api-key') == 'chonespuue42'):
            return '2'
        else:
            if args.get('command') not in [str(i) for i in range(1, 7)]:
                return '3'
            else:
                return function_switch(args)


def function_switch(args):
    switcher = {
        '1': update_parameters,
        '2': add_subscription,
        '3': remove_subscription,
        '4': replace_subscription,
        '5': subscriptions_list,
        '6': hosts_list,
        '7': send_message,
    }
    func = switcher.get(args.get('command'))
    return func(args, db)


def update_parameters(args, db):
    if not (args.get('serial-no')):
        return '4'
    elif not (cursor.execute("SELECT * FROM `host` WHERE `mac_address`='%s';" % args.get('serial-no'))):
        return '5'
    elif not (args.get('status')) and not (args.get('address')) and \
            not (args.get('name')) and not (args.get('cn')) and not (args.get('info')):
        return '7'
    elif args.get('status') and args.get('status') not in ['0', '1']:
        return '6'
    else:
        cursor.execute("UPDATE `host` SET `name` = '%s', `cn` = '%s', `address` = '%s', \
	    `info` = '%s', `is_active` = '%s' WHERE `mac_address` = '%s';" % \
                       (args.get('name'), args.get('cn'), args.get('address'), \
                        args.get('info'), args.get('status'), args.get('serial-no')))
        db.commit()
        return '100'


def add_subscription(args, db):
    if not (args.get('serial-no')):
        return '4'
    elif not (cursor.execute("SELECT `is_active` FROM `host` WHERE `mac_address`='%s';" % args.get('serial-no'))):
        return '5'
    elif (cursor.fetchall()[0][0] == 0):
        return '6'
    elif not (args.get('type')):
        return '7'
    elif args.get('type') not in ['1', '2']:
        return '8'
    elif not (args.get('package')):
        return '9'
    elif not (cursor.execute("SELECT * FROM `package` WHERE `code` = '%s' AND `is_active` = '1';" % \
                                     args.get('package'))):
        return '10'
    elif not (args.get('start')):
        return '11'
    elif not (datetime_convert(args.get('start'))):
        return '12'
    elif not (args.get('stop')):
        return '13'
    elif not (datetime_convert(args.get('stop'))):
        return '14'
    elif datetime_convert(args.get('stop')) <= datetime_convert(args.get('start')):
        return '15'
    else:
        if int(args.get('type')) == 1:
            type_ = 'regular'
        else:
            type_ = 'additional'
        cursor.execute(
            "INSERT INTO `subscribe` (`id`, `host`, `type`, `package`, `start`, `stop`, `info`, `is_active`)" + \
            " VALUES (NULL, '%s', '%s', '%s', '%s', '%s', '%s', '1');" % \
            (args.get('serial-no'), type_, args.get('package'), \
             datetime_convert(args.get('start')), datetime_convert(args.get('stop')), \
             args.get('info')))
        db.commit()
        return str(cursor.lastrowid)


def remove_subscription(args, db):
    if not (args.get('serial-no')):
        return '4'
    else:
        if args.get('package'):
            if not (cursor.execute("SELECT * FROM `package` WHERE `code` = '%s' AND `is_active` = '1';" % \
                                           args.get('package'))):
                return '5'
            else:
                where_package = "AND `package` = '%s'" % args.get('package')
        else:
            where_package = ''
        if args.get('subscription-id'):
            if not (args.get('subscription-id').isdigit()):
                return '6'
            else:
                where_id = "AND `id` = '%s'" % args.get('subscription-id')
        else:
            where_id = ''
        res = cursor.execute(
            "UPDATE `subscribe` SET `is_active` = '0' WHERE `host` = '%s' %s %s AND `is_active` = '1';" % \
            (args.get('serial-no'), where_package, where_id))
        db.commit()
        if res:
            return '100'
        else:
            return '7'


def replace_subscription(args, db):
    if not (args.get('serial-no-src')):
        return '4'
    elif not (cursor.execute("SELECT `is_active` FROM `host` WHERE `mac_address`='%s';" % args.get('serial-no-src'))):
        return '5'
    elif (cursor.fetchall()[0][0] == 0):
        return '6'
    if not (args.get('serial-no-dst')):
        return '7'
    elif not (cursor.execute("SELECT `is_active` FROM `host` WHERE `mac_address`='%s';" % args.get('serial-no-src'))):
        return '8'
    elif (cursor.fetchall()[0][0] == 0):
        return '9'
    elif not (cursor.execute("SELECT * FROM `subscribe` WHERE `is_active`='%s';" % 1)):
        return '10'
    else:
        cursor.execute("UPDATE `subscribe` SET `host`='%s' WHERE `host`='%s';" % (
        args.get('serial-no-dst'), args.get('serial-no-src')))
        db.commit()
        return '100'


def subscriptions_list(args, db):
    if args.get('serial-no') in args.values():
        sql = "SELECT * FROM `subscribe` WHERE `host`='%s';" % args.get('serial-no')
    else:
        sql = "SELECT * FROM `subscribe`;"
    if not (cursor.execute(sql)):
        return '4'
    else:
        data = cursor.fetchall()
        List = ""
        for row in data:
            if row[4] < datetime.now() and row[5] > datetime.now():
                is_running = 'true'
            else:
                is_running = 'false'
            if row[7] == 1:
                is_removed = 'false'
            else:
                is_removed = 'true'
            List += "%s;%s;%s;%s;0;%s;%s;%s;%s\n" % \
                    (row[1], row[0], row[3], row[2], "T".join(str(row[4]).split(' ')), "T".join(str(row[5]).split(' ')),
                     is_running, is_removed)
        return List


def hosts_list(args, db):
    if args.get('serial-no') in args.values():
        sql = "SELECT * FROM `host` WHERE `mac_address`='%s';" % args.get('serial-no')
    else:
        sql = "SELECT * FROM `host`;"
    if not (cursor.execute(sql)):
        return '4'
    else:
        data = cursor.fetchall()
        List = ""
        for row in data:
            if row[5] == 0:
                status = 'not-active'
            else:
                status = 'active'
            List += '%s;%s;"%s";"%s";"%s";"%s"\n' % (row[0], status, row[1], row[2], row[3], row[4])
        return List


def send_message(args, db):
    return 100


def datetime_convert(string):
    try:
        res = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            res = datetime.fromtimestamp(int(string))
        except ValueError:
            return 0
    now = datetime.now()
    if res < now:
        return datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strftime(res, "%Y-%m-%d %H:%M:%S")

