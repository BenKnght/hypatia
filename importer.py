from Config import logger
from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaParser import HypatiaParser
import Config


def run(input_file):
    c = MySQL.get_connection('astronomy_test')
    p = HypatiaParser(input_file)
    if c:
        for star, elements in p.next():
            try:
                star.upsert(c)
                logger.info('Saved star, "%s"\n', star.columns['hip'])
                for catalogue, composition in elements:
                    cid = catalogue.upsert(c)
                    composition.set('hip', star.columns['hip'])
                    composition.set('cid', cid)
                    composition.upsert(c)
            except Exception as e:
                logger.exception('Saving star failed: "%s"', e)
        c.close()


if __name__ == '__main__':
    Config.setup_logging()
    run('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    # run('/Volumes/350GB/Projects/RA/Assets/hypatia_norm_16_01_10.txt')
