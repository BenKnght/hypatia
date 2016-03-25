import logging

from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaParser import HypatiaParser
import Config


def main():
    Config.setup_logging()
    c = MySQL.get_connection('astronomy_test')
    p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    # p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/hypatia_norm_16_01_10.txt')
    if c:
        for star, elements in p.next():
            try:
                star.upsert(c)
                logging.info('Saved star, "%s"\n', star.columns['hip'])
                for catalogue, composition in elements:
                    cid = catalogue.upsert(c)
                    composition.set('hip', star.columns['hip'])
                    composition.set('cid', cid)
                    composition.upsert(c)
            except Exception as e:
                logging.exception('Saving star failed: "%s"', e)
        c.close()


if __name__ == '__main__':
    main()
