#!/usr/local/bin/python
# -*- coding: utf-8  -*-

from datetime import datetime


class Event:
    def __init__(self, time, message, channel):
        self.time = time
        self.message = str(message)
        self.channel = channel


class Log:
    def __init__(self):
        self.Events = [Event(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), 'Starting logging', None)]

    def event(self, channel, data, e_type):
        time = ux2date(str(data["timestamp"]))
        if e_type == "init":
            message = "Initializing stream: %s, %s, %s\n" % (
                data["channel"]["input"],
                data["channel"]["output"],
                data["channel"]["type"]
            )
        else:
            types = {
                "cc": "CC errors(%s)" % data["cc_error"],
                "pes": "PES errors(%s)" % data["pes_error"],
                "switch": "Changes active input %s" % data["input_id"]
            }
            message = types[e_type]
        self.Events.insert(0, Event(time, message, channel))

    def selection(self, channel):
        sample = []
        for event in self.Events[:-1]:
            if event.channel.sid == channel:
                sample.append(event)
        return sample


def ux2date(unixtime):
    return datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')
