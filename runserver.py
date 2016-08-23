#!/usr/local/bin/python
# -*- coding: utf-8  -*-

from flask_app import app

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug = True)