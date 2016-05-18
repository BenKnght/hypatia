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
from Utils.utils import median
from Utils.utils import upsert_dict_arr
from Utils.utils import upsert

app = Flask(__name__)

LOG_DIR = os.environ['LOGFILES_PATH'] if 'LOGFILES_PATH' in os.environ else './logs/'
UPLOADS_DIR = os.environ['DATAFILES_PATH'] if 'DATAFILES_PATH' in os.environ else './uploads/'
DATABASE = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else 'astronomy'


# HTML Services
@app.route('/')
def index():
    # return render_template('import.html')
    return explore()


@app.route('/import')
def import_data():
    return render_template('import.html')


@app.route('/visualize')
def visualize():
    return render_template('visualization.html')


@app.route('/explore')
def explore():
    return render_template('explore.html')


@app.route('/log/<filename>')
def send_logfile(filename):
    return send_from_directory(LOG_DIR, filename)


@app.route('/partials/<filename>')
def send_partial(filename):
    return render_template('partials/%s' % (filename,))


# Services
@app.route('/upload', methods=['POST'])
def upload():
    """
    Imports a file and saves to DB
    :return:
    """
    datafile = request.files['file']
    c = MySQL.get_connection(DATABASE)
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


@app.route('/stars/<int:page>/<int:limit>')
def stars(page, limit):
    """
    Retrieve requested number of stars of a given page satisfying a condition
    :param page: page number
    :param limit: number of stars in this page
    :return:
    """
    try:
        # TODO: Possible SQL injection due to WHERE clause
        query = "SELECT * FROM star WHERE {} LIMIT %s OFFSET %s".format(request.args.get("query") or "1 = 1")
        db_res = MySQL.execute(DATABASE, query, [limit, page * limit])
        index_of_hip = db_res['columns'].index('hip')
        resp = {row[index_of_hip]: dict(zip(db_res['columns'], [str(t) if type(t) is bytearray else t for t in row]))
                for row in db_res['rows']}
        return jsonify({'stars': resp, "status": {"message": "Fetched %s stars" % (len(resp),)}})
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


@app.route('/plots/composition/', methods=['POST'])
def composition_scatter():
    """
    Median composition of requested elements for the requested star considering common catalogs
    POST BODY:
    {
        stars: [required] comma separated list of hips
        elements: [required] comma separated list of elements for which compositions are required
        catalogs: [optional] comma separated list of catalogs to include if provided, else all will be used
    }
    :return: {hip1: {FeH: 0.5, OH: -0.07, ...}, {hip2: {FeH: 0.09, ...}}
    """
    try:
        stars = map(lambda s: s.strip(), request.json['stars'])
        elements = map(lambda e: e.strip(), request.json['elements'])
        catalogs = map(lambda c: c.strip(), request.json.get('catalogs', []))
        query = """SELECT
                      t1.hip,
                      t1.cid,
                      t1.element,
                      t1.value
                    FROM composition t1
                    INNER JOIN composition t2
                      ON t1.cid = t2.cid
                      AND t1.element <> t2.element
                      AND t1.hip = t2.hip
                      AND t1.hip IN (%s)
                      AND t1.element IN (%s)
                      AND t2.element IN (%s) %s;"""
        in_str_stars = ','.join(['%s'] * len(stars))
        in_str_elems = ','.join(['%s'] * len(elements))
        in_str_cats = ','.join(['%s'] * len(catalogs))
        catalog_query = 'AND t1.cid IN (%s);' % in_str_cats if len(catalogs) > 0 else ''
        db_res = MySQL.execute(DATABASE, query % (in_str_stars, in_str_elems, in_str_elems, catalog_query),
                               stars + elements + elements + catalogs)

        resp = {}
        selected_catalogs = set()
        for row in db_res['rows']:
            upsert_dict_arr(resp, row[0], row[2], row[3])
            selected_catalogs.add(row[1])
        for star in resp:
            for e in resp[star]:
                resp[star][e] = median(resp[star][e])
        return jsonify({'stars': resp, 'catalogs': _catalogs_for_ids(selected_catalogs),
                        "status": {"message": "Fetched %s stars" % len(resp)}})
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


@app.route('/planets/', methods=['POST'])
def planets():
    """
    Retrieves planets for the given hips
    POST BODY
    {
        stars: [required] comma separated list of hips
    }
    :return: planets: {hip1: [{planet1_prop1: value1, ...}]}
    """
    stars = map(lambda s: s.strip(), request.json['stars'])
    query = "SELECT `name`, hip, m_p, p, e, a FROM planet WHERE hip IN (%s);"
    in_str = ','.join(['%s'] * len(stars))
    db_res = MySQL.execute(DATABASE, query % in_str, stars)
    resp = {}
    for r in db_res['rows']:
        upsert(resp, r[1], dict(zip(db_res['columns'], r)))
    return jsonify({'planets': resp, "status": {"message": "Fetched %s planets" % (len(resp),)}})


@app.route('/catalog/<ids>')
def catalogs(ids):
    """
    Fetch catalogue names for given IDs
    :param ids: comma separated string of catalog IDs
    :return: {catalogs: [(id1, catalog_name1), (id2, catalog_name2),...]}
    """
    db_res = _catalogs_for_ids([id.strip() for id in ids.split(',')])
    return jsonify({'catalogs': db_res, "status": {"message": "Fetched %s catalogs" % len(db_res)}})


def _catalogs_for_ids(ids):
    query = "SELECT id, author_year FROM catalogue WHERE id IN (%s);"
    in_str = ','.join(['%s'] * len(ids))
    db_res = MySQL.execute(DATABASE, query % in_str, ids)['rows']
    return db_res


@app.route('/star/<hip>/elements')
def elements_of_star(hip):
    """
    Fetches the elements of a star
    :param hip: hip of the star
    :return:
    """
    try:
        query = "SELECT DISTINCT element FROM composition WHERE hip = %s"
        res = map(lambda e: e[0], MySQL.execute(DATABASE, query, [hip])['rows'])
        return jsonify({'elements': res})
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


@app.route('/star/<hip>/compositions')
def compositions_of_star(hip):
    """
    Retrieves composition of a star
    If an element has multiple values from different catalogs, average value is returned
    :param hip: hip of the star
    :return: {FeH: 0.5, OH: -0.6}
    """
    try:
        elements = request.args.getlist('elements')
        in_clause = ','.join(['%s'] * len(elements))
        query = """SELECT element, AVG(value)
                    FROM composition WHERE hip = %s AND element IN ({})
                    GROUP BY element;""".format(in_clause)
        res = {}
        for k, v in MySQL.execute(DATABASE, query, [hip] + elements)['rows']:
            res[k] = v
        return jsonify(res)
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


def main():
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
