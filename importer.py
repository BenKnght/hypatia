from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaParser import HypatiaParser


def main():
    c = MySQL.get_connection()
    p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    if c:
        for star, elements in p.next():
            try:
                star.upsert(c)
                for catalogue, composition in elements:
                    cid = catalogue.upsert(c)
                    composition.set('hip', star.columns['hip'])
                    composition.set('cid', cid)
                    composition.upsert(c)
            except:
                raise
                # TODO: Log failed save
                pass
        c.close()


if __name__ == '__main__':
    main()
