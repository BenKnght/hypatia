from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaParser import HypatiaParser


def main():
    c = MySQL.get_connection()
    p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    if c:
        for star, elements in p.next():
            try:
                star.save(c)
                for catalogue, composition in elements:
                    # TODO Start from here - Check if composition and catalogue are saving correctly
                    cid = catalogue.save()
                    composition.set('hip', star.columns['hip'])
                    composition.set('cid', cid)
                    composition.save()
            except:
                raise
                # TODO: Log failed save
                pass
        c.close()


if __name__ == '__main__':
    main()
