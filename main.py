import sqlite3, csv
from sqlite3 import Error

def openConnection(_dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Open database: ", _dbFile)

    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
        print("success")
    except Error as e:
        print(e)

    print("++++++++++++++++++++++++++++++++++")

    return conn


def closeConnection(_conn, _dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Close database: ", _dbFile)

    try:
        _conn.close()
        print("success")
    except Error as e:
        print(e)

    print("++++++++++++++++++++++++++++++++++")


def dropTables(con):
    con.execute("DROP TABLE IF EXISTS SeattleRainfall")
    con.execute("DROP TABLE IF EXISTS AnnualReport")
    con.execute("DROP TABLE IF EXISTS MonthlyReport")
    con.execute("DROP TABLE IF EXISTS DailyReport")
    con.execute("DROP TABLE IF EXISTS RangedReport")

    con.commit()


def createTables(con):
    print("++++++++++++++++++++++++++++++++++")
    print("Creating tables")

    try:
        sql = """ 
            CREATE TABLE IF NOT EXISTS SeattleRainfall (
                DATE DATE NOT NULL, 
                PRCP REAL NOT NULL, 
                TMAX INT NOT NULL, 
                TMIN INT NOT NULL, 
                RAIN CHAR NOT NULL
            ) """
        con.execute(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS AnnualReport (
                ar_year     INT NOT NULL, 
                ar_avgPrcp   REAL NOT NULL, 
                ar_avgTemp  REAL NOT NULL, 
                ar_numRainDays INT NOT NULL 
            ) """
        con.execute(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS MonthlyReport (
                mr_year INT NOT NULL, 
                mr_month INT NOT NULL, 
                mr_avgPrcp  REAL NOT NULL,
                mr_avgTemp  REAL NOT NULL,
                mr_numRainDays INT NOT NULL
            ) """
        con.execute(sql)
        
        sql = """
            CREATE TABLE IF NOT EXISTS DailyReport (
                dr_date DATE NOT NULL, 
                dr_prcp REAL NOT NULL,
                dr_tmax INT NOT NULL,
                dr_tmin INT NOT NULL, 
                dr_rain CHAR NOT NULL
            ) """
        con.execute(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS RangedReport (
                rr_startDate DATE NOT NULL, 
                rr_endDate  DATE NOT NULL, 
                rr_avgPrcp  REAL NOT NULL, 
                rr_avgTemp  REAL NOT NULL,
                rr_numRainDays  INT NOT NULL
            ) """ 
        con.execute(sql)

        con.commit()
        print("Tables successfully created")

    except Error as e:
        con.rollback()
        print(e)

    print("++++++++++++++++++++++++++++++++++")


def populateSeattleRainfall(_conn):
    print("++++++++++++++++++++++++++++++++++")
    print("Populating SeattleRainfall")
    
    try:
        cur = _conn.cursor()

        with open('Data/seattleWeather_1948-2017.csv','r') as fin: 
            # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(fin) # comma is default delimiter
            to_db = [(i['DATE'], i['PRCP'], i['TMAX'], i['TMIN'], i['RAIN']) for i in dr]

        cur.executemany("INSERT INTO SeattleRainfall VALUES (?, ?, ?, ?, ?);", to_db)
        _conn.commit()
        print("Bulk loading was successful")

    except Error as e:
        _conn.rollback()
        print(e)

    print("++++++++++++++++++++++++++++++++++")

def getAnnualReport(con):
    print("Enter a year: ")
    year = input()

    sql = """ 
        SELECT AVG(PRCP), (AVG(TMAX)+AVG(TMIN))/2, (
            SELECT COUNT(RAIN)
            FROM SeattleRainfall
            WHERE RAIN = 'TRUE' AND strftime('%Y', DATE) = ?
        ) rainDays
        FROM SeattleRainfall
        WHERE strftime('%Y', DATE) = ? 
        """
    con.execute(sql, (year, year,)) 

    cur = con.cursor()
    row = cur.fetchall()

    print(row)

def main():
    database = r"Data/database.sqlite"

    conn = openConnection(database)

    with conn:
        #dropTables(conn)
        #createTables(conn)

        #populateSeattleRainfall(conn)

        getAnnualReport(conn)

    closeConnection(conn, database)

if __name__ == '__main__':
    main()