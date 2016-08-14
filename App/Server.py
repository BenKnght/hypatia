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
from Utils.utils import median, mean
from Utils.utils import upsert_dict_arr
from Utils.utils import upsert
from Model.Star import Star
from Model.Planet import Planet

app = Flask(__name__)

LOG_DIR = os.environ['LOGFILES_PATH'] if 'LOGFILES_PATH' in os.environ else './logs/'
UPLOADS_DIR = os.environ['DATAFILES_PATH'] if 'DATAFILES_PATH' in os.environ else './datafiles/'
DATABASE = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else 'astronomy'


# HTML Services
@app.route('/')
def index():
    # return import_data()
    return explore()


@app.route('/import')
def import_data():
    return render_template('import.html')


@app.route('/visualize')
def visualize():
    return render_template('visualization.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/ack')
def ack():
    return render_template('acknowledgement.html')


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
            Importer.run(filepath, c, {"normalization": request.form['normalization']})

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
        query = "SELECT * FROM star WHERE {} ORDER BY `hip` LIMIT %s OFFSET %s".format(
            request.args.get("query") or "1 = 1")
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
        normalization: [required] the type of solar normalization
        stars: [required] comma separated list of hips
        elements: [required] comma separated list of elements for which compositions are required
        catalogs: [optional] comma separated list of catalogs (author_year column) to exclude if provided, else all will be used
    }
    :return: {hip1: {FeH: {mdn: 0.5, avg: 0.56}, OH: {mdn: -0.07, avg: 0}, ...}, {hip2: {FeH: {mdn: 0.09, avg: 0.1}, ...}}
    """
    try:
        solarnorm = request.json['normalization']
        stars = map(lambda s: s.strip(), request.json['stars'])
        elements = map(lambda e: e.strip(), request.json['elements'])
        catalogs = map(lambda c: c.strip(), request.json.get('catalogs', []))
        query = """SELECT
                      t1.hip,
                      t1.cid,
                      t1.element,
                      t1.value
                    FROM composition t1, catalogue c, composition t2
                      WHERE t1.solarnorm = '%s' AND t2.solarnorm = '%s'
                      AND t1.cid = t2.cid
                      AND t1.element <> t2.element
                      AND t1.hip = t2.hip
                      AND t1.hip IN (%s)
                      AND t1.element IN (%s)
                      AND t2.element IN (%s)
                      AND t1.cid = c.id %s;"""
        in_str_stars = ','.join(['%s'] * len(stars))
        in_str_elems = ','.join(['%s'] * len(elements))
        in_str_cats = ','.join(['%s'] * len(catalogs))
        catalog_query = 'AND c.author_year NOT IN (%s)' % in_str_cats if len(catalogs) > 0 else ''
        db_res = MySQL.execute(DATABASE, query % (solarnorm, solarnorm, in_str_stars, in_str_elems, in_str_elems,
                                                  catalog_query), stars + elements + elements + catalogs)

        resp = {}
        for row in db_res['rows']:
            upsert_dict_arr(resp, row[0], row[2], row[3])
        for star in resp:
            for e in resp[star]:
                resp[star][e] = {'mdn': median(resp[star][e]), 'avg': mean(resp[star][e])}
        return jsonify({'stars': resp, "status": {"message": "Fetched %s stars" % len(resp)}})
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


@app.route('/stellar-props/', methods=['POST'])
def stellar_props():
    """
    Retrieve stellar properties
    POST BODY:
    {
        properties: [optional] one or more of properties of a star, e.g. [u, w, dist, v, mass]
        stars: [required] a list of hips for whose the above properties are required
    }
    where,
    mass => stellar mass
    if properties are ignored, all properties are returned
    :return: {hip1: {mass: 867, dist: 0.889}, hip2: {mass: 773, dist: 0.8772}}
    """
    try:
        stars = map(lambda s: s.strip(), request.json['stars'])
        props = map(lambda s: s.strip(), request.json.get('properties', Star.DEFAULTS.keys()))
        props_cols_map = {'u': 'u', 'w': 'w', 'dist': 'dist', 'v': 'v', 'mass': 'mass'}
        columns = [props_cols_map.get(p, p) for p in props]
        query = "SELECT hip, {} FROM star WHERE hip IN (%s);".format(', '.join(columns))
        resp = tuples_as_dict(query, stars, 0)
        return jsonify({'stars': resp, "status": {"message": "Fetched info for %s stars" % len(resp)}})
    except Exception as err:
        logger.exception(err)
        return jsonify({"status": {"message": "Something went wrong"}}), 500


@app.route('/planet-props/', methods=['POST'])
def planet_props():
    """
    **** DEPRECATED: Use /planets/ instead ****

    Retrieve planet properties
    POST BODY:
    {
        properties: [optional] one or more of properties of a planet, e.g. [name, mass, hip, p, e, a]
        stars: [required] a list of hips whose planets' properties are returned
    }
    where,
    mass => planet mass
    if properties are ignored, all properties are returned
    :return: {hip1_planet1: {m_p: 867, p: 0.889}, hip2_planet2: {m_p: 773, p: 0.8772}}
    """
    try:
        stars = map(lambda s: s.strip(), request.json['stars'])
        props = map(lambda s: s.strip(), request.json.get('properties', Planet.DEFAULTS.keys()))
        props_cols_map = {'name': 'name', 'mass': 'm_p as mass', 'p': 'p', 'e': 'e', 'a': 'a'}
        columns = [props_cols_map.get(p, p) for p in props]
        query = """SELECT
                      CONCAT(s.hip, ' [', p.name, ']') as star_planet, {}
                    FROM planet p
                    INNER JOIN star s
                      ON s.hip = p.hip
                    WHERE s.hip IN (%s)""".format(', '.join(columns))
        resp = tuples_as_dict(query, stars, 0)
        return jsonify({'planets': resp, "status": {"message": "Fetched info for %s planets" % len(resp)}})
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
    resp = tuples_as_dict(query, stars, 1)
    return jsonify({'planets': resp, "status": {"message": "Fetched %s planets" % len(resp)}})


@app.route('/elements/', methods=['POST'])
def elements():
    """
    Retrieves elements for the given hips
    POST BODY
    {
        stars: [required] comma separated list of hips
    }
    :return: elements: {hip1: [{elem_prop1: value1, ...}]}
    """
    stars = map(lambda s: s.strip(), request.json['stars'])
    query = """SELECT c.hip, author_year as catalogue, element, `value`
                FROM composition c INNER JOIN catalogue ca ON c.cid = ca.id
                WHERE c.hip IN (%s);"""
    resp = tuples_as_dict(query, stars, 0)
    return jsonify({'elements': resp, "status": {"message": "Fetched %s elements" % len(resp)}})


def tuples_as_dict(query, entities, key_col):
    """
    Fetches the tuples and converts to a dictionary based on the key column from the result
    :param query: query as string
    :param entities: input entities. Eg: hips
    :param key_col: index of the key column in the returned tuples
    :return: a dictionary with array of values for each key col
    """
    in_str = ','.join(['%s'] * len(entities))
    db_res = MySQL.execute(DATABASE, query % in_str, entities)
    resp = {}
    for r in db_res['rows']:
        upsert(resp, r[key_col], dict(zip(db_res['columns'], r)))
    return resp


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
