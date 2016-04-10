#!/bin/env python
# encoding: utf-8

import os
import time
import logging
from flask import jsonify
from flask import Flask, request
from flask import render_template
from flask import send_from_directory

import Importer
from DataSource.MySQLDataSource import MySQL
import Config
from Config import logger

app = Flask(__name__)

LOG_DIR = os.environ['LOGFILES_PATH']
UPLOADS_DIR = os.environ['DATAFILES_PATH']


# HTML Services
@app.route('/')
def index():
    # return render_template('import.html')
    return visualize()


@app.route('/visualize')
def visualize():
    return render_template('visualization.html')


@app.route('/log/<filename>')
def send_logfile(filename):
    return send_from_directory(LOG_DIR, filename)


@app.route('/partials/<filename>', methods=['GET'])
def send_partial(filename):
    return render_template('partials/%s' % (filename,))


# Services
@app.route('/upload', methods=['POST'])
def upload():
    datafile = request.files['file']
    database = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else 'astronomy_test'
    c = MySQL.get_connection(database)
    if datafile:
        try:
            logfile = os.path.splitext(datafile.filename)[0] + str(
                int(time.time())) + '.log'  # given name + current timestamp
            f = logging.FileHandler(os.path.join(LOG_DIR, logfile), 'w')
            Config.setup_logging(f)

            filepath = os.path.join(UPLOADS_DIR, datafile.filename)
            datafile.save(filepath)  # to file system
            Importer.run(filepath, c)

            logger.removeHandler(f)
            f.close()
            return jsonify({"name": datafile.filename, 'log': logfile})
        finally:
            c.close()


@app.route('/star/<hip>/elements', methods=['GET'])
def elements_of_star(hip):
    return jsonify({'data': {1: 'FeH', 2: 'NiH', 3: 'BeH'}})


def main():
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
