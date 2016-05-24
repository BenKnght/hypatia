from Config import logger
from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaExoParser import HypatiaExoParser
import Config


def run(input_file, c):
    p = HypatiaExoParser(input_file)
    if c:
        for star, elements, planets in p.next():
            try:
                star.upsert(c)
                logger.info('Saved star, "%s"\n', star.columns['hip'])
                for catalogue, composition in elements:
                    # Assumption 251024: Because of the way the records are updated, if a catalogue is updated say
                    # from 'FeH 0.3 [Adamow et al. (2015)]' to 'FeH 0.3 [Adamow et al. (2016)]' a new catalogue is
                    # added and the particular composition for that catalogue will still be present with
                    # old catalogue in the composition table. For the above example the table composition will have
                    # 2 entries, one with 2015 catalogue and one with 2016
                    # Fix: Delete the star completely and add it again. Deleting a star, also deletes the corresponding
                    # composition elements, but catalogues are retained as other stars may still use it!

                    cid = catalogue.upsert(c)
                    composition.set('hip', star.columns['hip'])
                    composition.set('cid', cid)
                    composition.upsert(c)
                for planet in planets:
                    planet.set('hip', star.columns['hip'])
                    planet.upsert(c)
            except:
                logger.exception('Saving star failed: "%s"', star.columns['hip'])
        c.close()


def main():
    Config.setup_logging()
    c = MySQL.get_connection('astronomy_test')
    # run('./Assets/test_inp.txt', c)
    run('./Assets/exo_test_inp.txt', c)
    # run('./Assets/hypatia_norm_16_01_10.txt', c)


if __name__ == '__main__':
    main()
