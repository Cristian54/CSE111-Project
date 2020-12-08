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
    #con.execute("DROP TABLE IF EXISTS SeattleRainfall")
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
                mr_monthYear DATE NOT NULL, 
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
                rr_maxTemp  REAL NOT NULL,
                rr_minTemp  REAL NOT NULL,
                rr_numRainDays  INT NOT NULL,
                rr_totalDays    INT NOT NULL
            ) """ 
        con.execute(sql)

        con.commit()
        print("Tables successfully created")

    except Error as e:
        con.rollback()
        print(e)

    print("++++++++++++++++++++++++++++++++++")

def deleteTables(conn):
    conn.execute("DELETE FROM AnnualReport")
    conn.execute("DELETE FROM DailyReport")
    conn.execute("DELETE FROM RangedReport")
    
    conn.commit()

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
    year = input("Enter a year: ")
    
    sql = """ 
        SELECT ROUND(AVG(PRCP), 3), COUNT(RAIN), (
            SELECT ROUND((AVG(TMAX)+AVG(TMIN))/2, 3)
            FROM SeattleRainfall
            WHERE strftime('%Y', DATE) = ?
        ) avgTemp
        FROM SeattleRainfall
        WHERE RAIN = 'TRUE' AND strftime('%Y', DATE) = ?
        """
    cur = con.cursor()
    cur.execute(sql, (year, year,)) 
    report = cur.fetchone()
    
    cur.execute("""INSERT INTO AnnualReport VALUES(?, ?, ?, ?)""", (year, report[0], report[2], report[1],))
    con.commit()
    
    print("Annual Report for the year", year, ": \n Average precipitation (in inches):", report[0], "\n Average temperature (F):", report[2], "\n Total number of rainy days:", report[1])

def getMonthlyReport(con):
    year = input("Enter a year: ")
    
    sql = """ 
    SELECT COUNT(RAIN), ROUND(AVG(PRCP), 3)
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE' AND strftime('%Y', DATE) = ?
    GROUP BY strftime('%m', DATE) """
    
    cur = con.cursor()
    cur.execute(sql, (year,))
    rainPrcp = cur.fetchall()
    
    sql = """ 
    SELECT strftime('%m-%Y', DATE), ROUND((AVG(TMAX)+AVG(TMIN))/2, 3)
    FROM SeattleRainfall
    WHERE strftime('%Y', DATE) = ?
    GROUP BY strftime('%m', DATE) """ 
    
    cur.execute(sql, (year,))
    monthTemp = cur.fetchall()
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] 
    print("Monthly report for the year", year,":")
    
    for month, row, roww in zip(months, monthTemp, rainPrcp):
        print(month, ":\n Average temperature (F):", row[1], "\n Number of rainy days:", roww[0], "\n Average precipitation (in inches):", roww[1])
    
def getDailyReport(con):
    year = input("Enter a year: ")
    month = input("Enter a month (Numerically): ")
    date = year + "-" + month
    
    sql = """
    SELECT *
    FROM SeattleRainfall
    WHERE strftime('%Y-%m', DATE) = ?
    GROUP BY strftime('%d', DATE) """
    
    cur = con.cursor()
    cur.execute(sql, (date,))
    report = cur.fetchall()
    
    print("Daily report for", month + "-" + year)
    
    for row in report:
        if row[4] == 'TRUE':
            rain = 'Rained'
        else:
            rain = 'Did not rain'
            
        print(row[0], "\n", rain, "| Precipitation:", row[1], "| Highest/Lowest temperature (F):", row[2], "/", row[3])

def getRangedReport(con):
    startDate = input("Enter a starting date (YYYY-MM-DD): ") 
    endDate = input("Enter an end date (YYYY-MM-DD): ")
    
    sql = """ 
    SELECT COUNT(RAIN), ROUND(AVG(PRCP), 3)
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE' AND (DATE >= ? AND DATE <= ?) """
    
    cur = con.cursor()
    cur.execute(sql, (startDate, endDate,))
    rainPrcp = cur.fetchone()
    
    sql = """
    SELECT ROUND((AVG(TMAX)+AVG(TMIN))/2, 3), COUNT(DATE), MAX(TMAX), MIN(TMIN)
    FROM SeattleRainfall
    WHERE DATE >= ? AND DATE <= ? """
    
    cur.execute(sql, (startDate, endDate,))
    tempDays = cur.fetchone()
    
    print()
    print("Report starting from", startDate, "and ending on", endDate, ": \n Average Precipitation (in inches):", 
          rainPrcp[1], "\n Average temperature (F):", tempDays[0], "\n Highest/Lowest temperature (F):", tempDays[2], "/", tempDays[3], "\n Number of rainy days:", rainPrcp[0], "\n Total number of days:", tempDays[1])

def getLeastOrMostRain(conn):
    choice = input("Do you want to list the years with the most/least rain, or get top single year? (list/single): ")
    print()
    
    cur = conn.cursor()
    
    if choice == "single":
        choice = input("Do you want to get the year with the most or least rain? (M/L): ")
        print()
        
        if choice == 'M':
            sql = """ 
                SELECT strftime('%Y', DATE), COUNT(RAIN)
                FROM SeattleRainfall
                WHERE RAIN = 'TRUE'
                GROUP BY strftime('%Y', DATE)
                ORDER BY COUNT(RAIN) DESC
                LIMIT 1 """

            cur.execute(sql)
            row = cur.fetchone()
            
            print("From 1948 to 2017, the year with the most rain in Seattle was", row[0], "with a total of", row[1], "rainy days.")

        elif choice == 'L':
            sql = """ 
                SELECT strftime('%Y', DATE), COUNT(RAIN)
                FROM SeattleRainfall
                WHERE RAIN = 'TRUE'
                GROUP BY strftime('%Y', DATE)
                ORDER BY COUNT(RAIN) ASC
                LIMIT 1 """

            cur.execute(sql)
            row = cur.fetchone()
            
            print("From 1948 to 2017, the year with the least rain in Seattle was", row[0], "with a total of", row[1], "rainy days.")
            
    elif choice == "list":
        choice = input("Do you want to list the years with the most or least rain? (M/L): ")
        print()
        
        if choice == "M":
            length = input("How many years do you want to list? (Total of 69 years available): ")
            print()

            sql = """ 
                SELECT strftime('%Y', DATE), COUNT(RAIN)
                FROM SeattleRainfall
                WHERE RAIN = 'TRUE'
                GROUP BY strftime('%Y', DATE)
                ORDER BY COUNT(RAIN) DESC
                LIMIT ? """

            cur.execute(sql, (length,))
            yearList = cur.fetchall()

            print("These are the top", length, "years with the most rain:")
            for year in yearList:
                print(year[0] + ":", year[1], "rainy days")
        
        elif choice == "L":
            length = input("How many years do you want to list? (Total of 69 years available): ")
            print()

            sql = """ 
                SELECT strftime('%Y', DATE), COUNT(RAIN)
                FROM SeattleRainfall
                WHERE RAIN = 'TRUE'
                GROUP BY strftime('%Y', DATE)
                ORDER BY COUNT(RAIN) ASC
                LIMIT ? """

            cur.execute(sql, (length,))
            yearList = cur.fetchall()

            print("These are the top", length, "years with the least rain: ")
            for year in yearList:
                print(year[0] + ":", year[1], "rainy days")
        

def userInpDates(conn):
    startY = input('starting year: ')
    startM = input('starting month: ')
    startD = input('starting day: ')
    start = startY + '-' + startM + '-' + startD

    endY = input('ending year: ')
    endM = input('ending month: ')
    endD = input('ending day: ')
    end = endY + '-' + endM + '-' + endD
    sql = """
    SELECT *
    FROM SeattleRainfall
    WHERE DATE >= ? and
    DATE <= ? """
    
    cur = conn.cursor()
    cur.execute(sql, (start, end))
    x = cur.fetchall()
    
    print("Data from " + start + " to " + end)
    for row in x:
        if row[4] == 'TRUE':
            rain = 'Rained'
        else:
            rain = 'Did not rain'
            
        print(row[0], "\n", rain, "| Precipitation:", row[1], "| Highest/Lowest temperature (F):", row[2], "/", row[3])

#num days rained and did not rain, not done yet
def rainDays (conn):
    sql = """ select count(rain1) as rained, count(rain2) as noRain
        from (
            select 
            case when rain = 'TRUE' then rain end as rain1,
            case when rain = 'FALSE' then rain end as rain2
            from SeattleRainfall
        ) as x
    """
    cur = conn.cursor()
    cur.execute(sql)
    x = cur.fetchall()
    #printing goes here
          
def main():
    database = r"Data/database.sqlite"

    conn = openConnection(database)

    with conn:
        dropTables(conn)
        createTables(conn)

        populateSeattleRainfall(conn)

<<<<<<< HEAD
        #getAnnualReport(conn)
        
        getLeastOrMostRain(conn)
        
        #getMonthlyReport(conn)
        
        #getDailyReport(conn)
        
        #getRangedReport(conn)
=======
        print("Options: \n1: get annual data of a specified year \n2: get the day with the most or least rain \n ")
        functions = 0
        functions = input("Choose what you would like to do: ")
        
        if functions == '1':
            getAnnualReport(conn)
        elif functions == '2':
            getLeastOrMostRain(conn)
        elif functions == '3':
            getMonthlyReport(conn)
        elif functions == '4':
            getDailyReport(conn)
        elif functions == '5':
            userInpDates(conn)
>>>>>>> daeea5ed50121eb1a1fe1d0195f7dfe0519dd45c
        
        #deleteTables(conn)

    closeConnection(conn, database)

if __name__ == '__main__':
    main()