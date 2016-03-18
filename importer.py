from DataSource.MySQLDataSource import MySQL
from Parser.HypatiaParser import HypatiaParser


def main():
    c = MySQL.get_connection()
    p = HypatiaParser('/Volumes/350GB/Projects/RA/Assets/test_inp.txt')
    if c:
        for star in p.next():
            try:
                star.save(c)
            except:
                # TODO: Log failed save
                pass
        c.close()


if __name__ == '__main__':
    main()
