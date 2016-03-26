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
import Config
from Config import logger

app = Flask(__name__)

LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), './logs')
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), './datafiles')


@app.route('/', methods=['GET'])
def index():
    return render_template('import.html')


@app.route('/visualize', methods=['GET'])
def visualize():
    return render_template('visualization.html')


@app.route('/log/<filename>', methods=['GET'])
def send_logfile(filename):
    return send_from_directory(LOG_DIR, filename)


@app.route('/upload', methods=['POST'])
def upload():
    datafile = request.files['file']
    if datafile:
        logfile = os.path.splitext(datafile.filename)[0] + str(
            int(time.time())) + '.log'  # given name + current timestamp
        f = logging.FileHandler(os.path.join(LOG_DIR, logfile), 'w')
        Config.setup_logging(f)

        filepath = os.path.join(UPLOADS_DIR, datafile.filename)
        datafile.save(filepath)  # to file system
        Importer.run(filepath)

        logger.removeHandler(f)
        f.close()
        return jsonify({"name": datafile.filename, 'log': logfile})


def main():
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
