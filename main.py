import sqlite3
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


def createTables(con):
    print("++++++++++++++++++++++++++++++++++")
    print("Creating tables")

    try:
        sql = """ 
            CREATE TABLE IF NOT EXISTS SeattleRainfall (
                DATE DATE NOT NULL, 
                PRPC REAL NOT NULL, 
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
                ar_numRainDays INT NOT NULL, 
                ar_rainPCT REAL NOT NULL
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
                dr_prpc REAL NOT NULL,
                dr_tmax INT NOT NULL,
                dr_tmin INT NOT NULL, 
                dr_rain CHAR NOT NULL
            ) """
        con.execute(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS RangedReport (
                rr_startDate DATE NOT NULL, 
                rr_endDate  DATE NOT NULL, 
                rr_avgPrpc  REAL NOT NULL, 
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

def main():
    database = r"Data/databse.sqlite"

    conn = openConnection(database)

    with conn:
        createTables(conn)

    closeConnection(conn, database)

if __name__ == '__main__':
    main()