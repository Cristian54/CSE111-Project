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
    year = input("\nEnter a year: ")
    
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
    
    print("\nAnnual Report for the year", year, ": \n Average precipitation (in inches):", report[0], "\n Average temperature (F):", report[2], "\n Total number of rainy days:", report[1])

def getMonthlyReport(con):
    year = input("\nEnter a year: ")
    
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
    print("\nMonthly report for the year", year,":\n")
    
    for month, row, roww in zip(months, monthTemp, rainPrcp):
        print(month, ":\n  Average temperature (F):", row[1], "\n  Number of rainy days:", roww[0], "\n  Average precipitation (in inches):", roww[1], "\n")
    
def getDailyReport(con):
    year = input("\nEnter a year: ")
    month = input("Enter a month (01-12): ")
    date = year + "-" + month
    
    sql = """
    SELECT *
    FROM SeattleRainfall
    WHERE strftime('%Y-%m', DATE) = ?
    GROUP BY strftime('%d', DATE) """
    
    cur = con.cursor()
    cur.execute(sql, (date,))
    report = cur.fetchall()
    
    print("\nDaily report for", month + "-" + year, ":\n")
    
    for row in report:
        if row[4] == 'TRUE':
            rain = 'Rained'
        else:
            rain = 'Did not rain'
            
        print("Date:", row[0], "|", rain, "| Precipitation:", row[1], "| Highest/Lowest temperature (F):", row[2], "/", row[3])

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
            
            print("From 1948 to 2017, the year with the most rain in Seattle was", row[0], "with a total of", row[1], "rainy days. \n")

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
            
            print("From 1948 to 2017, the year with the least rain in Seattle was", row[0], "with a total of", row[1], "rainy days. \n")
            
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

            print("\nThese are the top", length, "years with the most rain:")
            for year in yearList:
                print(year[0] + ":", year[1], "rainy days")
        
        elif choice == "L":
            length = input("How many years do you want to list? (Total of 69 years available): ")

            sql = """ 
                SELECT strftime('%Y', DATE), COUNT(RAIN)
                FROM SeattleRainfall
                WHERE RAIN = 'TRUE'
                GROUP BY strftime('%Y', DATE)
                ORDER BY COUNT(RAIN) ASC
                LIMIT ? """

            cur.execute(sql, (length,))
            yearList = cur.fetchall()

            print("\nThese are the top", length, "years with the least rain: \n")
            for year in yearList:
                print(year[0] + ":", year[1], "rainy days")

def rainDays(conn):
    sql = """ 
    SELECT COUNT(*) as Rained, (
        SELECT COUNT(*)
        FROM SeattleRainfall
        WHERE RAIN = 'FALSE'
    ) NoRain
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE'
    """
    cur = conn.cursor()
    cur.execute(sql)
    rain = cur.fetchone()

    print("\nFrom 1948-01-01 to 2017-12-14, or 25,548 recorded days, Seattle had", rain[0], "days with rain and", rain[1], "days without rain.\n")

def getDayInAllYears(con):
    day = input("\nEnter a day (MM-DD): ")

    sql = """
    SELECT * 
    FROM SeattleRainfall
    WHERE strftime('%m-%d', DATE) = ? """

    cur = con.cursor()
    cur.execute(sql, (day,))
    days = cur.fetchall()

    for day in days:
        if day[4] == 'TRUE':
            rain = 'Rained'
        else:
            rain = 'Did not rain'

        print("Date:", day[0], "| Precipitation:", day[1], "| Max temperature (F):", day[2], "| Min temperature (F):", day[3], "|", rain)

def getColdestHottestDays(con):
    choice = input("\nDo you want to list the hottest or coldest days? (H/C): ")
    
    cur = con.cursor()
    if choice == 'H':
        length = input("\nHow many days do you want to list? ")
        rain = input("\nDo you want to list the hottest days where it rained? (Y/N): ")
        
        if rain == 'N': 
            sql = """ 
            SELECT DATE, MAX(TMAX)
            FROM SeattleRainfall
            WHERE RAIN = 'FALSE'
            GROUP BY strftime('%d', DATE) 
            ORDER BY MAX(TMAX) DESC
            LIMIT ? """
            
            cur.execute(sql, (length,))
            days = cur.fetchall()
            
            print("\nThe", length, "hottest days, from 1948 to 2017, in Seattle were:")
            for day in days:
                print("Date:", day[0], "| Temperature (F):", day[1])
                
        elif rain == 'Y':
            sql = """ 
            SELECT DATE, MAX(TMAX)
            FROM SeattleRainfall
            WHERE RAIN = 'TRUE'
            GROUP BY strftime('%d', DATE) 
            ORDER BY MAX(TMAX) DESC
            LIMIT ? """
            
            cur.execute(sql, (length,))
            days = cur.fetchall()
            
            print("\nThe", length, "hottest rainy days, from 1948 to 2017, in Seattle were:")
            for day in days:
                print("Date:", day[0], "| Temperature (F):", day[1]) 
        
    elif choice == 'C':
        length = input("\nHow many days do you want to list? ")
        rain = input("\nDo you want to list the coldest days with/without rain, or both? (R/NR/B): ")
        rain.upper()
        
        if rain == 'R':
            sql = """
            SELECT DATE, MIN(TMIN)
            FROM SeattleRainfall
            WHERE RAIN = 'TRUE'  
            GROUP BY strftime('%d', DATE) 
            ORDER BY MIN(TMIN) ASC
            LIMIT ? """
            
            cur.execute(sql, (length,))
            days = cur.fetchall()
            
            print("\nThe", length, "coldest rainy days, from 1948 to 2017, in Seattle were:")
            for day in days:
                print("Date:", day[0], "| Temperature (F):", day[1]) 
        
        elif rain == 'NR':
            sql = """
            SELECT DATE, MIN(TMIN)
            FROM SeattleRainfall
            WHERE RAIN = 'FALSE'  
            GROUP BY strftime('%d', DATE) 
            ORDER BY MIN(TMIN) ASC
            LIMIT ? """
            
            cur.execute(sql, (length,))
            days = cur.fetchall()
            
            print("\nThe", length, "coldest days, from 1948 to 2017, without rain in Seattle were:")
            for day in days:
                print("Date:", day[0], "| Temperature (F):", day[1])
        
        elif rain == 'B':
            sql = """
            SELECT DATE, MIN(TMIN), RAIN
            FROM SeattleRainfall
            WHERE RAIN = 'FALSE'  
            GROUP BY strftime('%d', DATE) 
            ORDER BY MIN(TMIN) ASC
            LIMIT ? """
            
            cur.execute(sql, (length,))
            days = cur.fetchall()
            
            print("\nThe", length, "coldest days from 1948 to 2017 in Seattle were:")
            for day in days:
                if day[4] == 'TRUE':
                    rain = 'Rained'
                else:
                    rain = 'Did not rain'
                print("Date:", day[0], "| Temperature (F):", day[1], "|", rain)

def insertIntoSeattleRainfall(conn):
    date = input("Enter the date (YYYY-MM-DD): ")
    prcp = input("Enter the precipitation: ")
    maxTemp = input("Enter the day's highest temperature (F): ")
    minTemp = input("Enter the day's lowest temperature (F): ")
    rain = input("Did it rain? (TRUE/FALSE): ")
    
    sql = """
    insert into SeattleRainfall(DATE, PRCP, TMAX, TMIN, RAIN)
    VALUES (?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    cur.execute(sql, (date, prcp, maxTemp, minTemp, rain,))
    conn.commit()

def modifySeattleRainfall(conn):
    currDate = input("Enter the day you are modifying (YYYY-MM-DD): ")
    newPrcp = input("Enter the day's precipitation: ")
    newMaxTemp = input("Enter the day's highest temperature (F): ")
    newMinTemp = input("Enter the day's lowest temperature (F): ")
    newRain = input("Did it rain? (TRUE/FALSE): ")
    sql = """
    update SeattleRainfall
    set PRCP = ?,
        TMAX = ?,
        TMIN = ?,
        RAIN = ?
    where DATE = ?
    """

    cur = conn.cursor()
    cur.execute(sql, (newPrcp, newMaxTemp, newMinTemp, newRain, currDate,))
    conn.commit()
           
def main():
    database = r"Data/database.sqlite"

    conn = openConnection(database)

    with conn:
        #dropTables(conn)
        #createTables(conn)

        #populateSeattleRainfall(conn)
        
        #deleteTables(conn)
        
        print("This program allows you to view rainfall statistics from the city of Seattle, WA. There is information dating back to 1948 all the way up to 2017. \n")
         
        functions = 1
        while functions != '0':
            print("-------------------------------------------------------------------")
            print("Below are the available options, each numbered to specify which option you want to choose: \n")
            
            options = ["(1) Annual Report: Get average data from a specified year", 
                       "(2) Monthly Report: Get an annual report broken down into months",
                       "(3) Daily Report: Get the data from every day in a specified month", 
                       "(4) Ranged Report: Get average data from specified start and end dates",
                       "(5) Get the single year with the most or least rain, or list a specified amount of years by most/least rain", 
                       "(6) Get the total number of days it rained and days it did not rain from 1948 to 2017",
                       "(7) Get the information from a specific day from every year available",
                       "(8) List the hottest or coldest days from the database, amount specificed by user",
                       "(9) Insert data into the database, e.g. a day prior to 1948 or after 2017",
                       "(10) Modify a specific day's data in the database"]
            
            print("Reports: \n ", options[0], "\n ", options[1], "\n ", options[2], "\n ", options[3])
            print("Other options: \n ", options[4], "\n ", options[5], "\n ", options[6], "\n ", options[7], "\n ", options[8], "\n ", options[9])
          
            functions = input("\nChoose what you would like to do: ")
            
            if functions == '1':
                getAnnualReport(conn)
            elif functions == '2':
                getMonthlyReport(conn)
            elif functions == '3':
                getDailyReport(conn)
            elif functions == '4':
                getRangedReport(conn)
            elif functions == '5':
                getLeastOrMostRain(conn)
            elif functions == '6':
                rainDays(conn)
            elif functions == '7':
                getDayInAllYears(conn)
            elif functions == '8':
                getColdestHottestDays(conn)
            elif functions == '9':
                insertIntoSeattleRainfall(conn)
            elif functions == '10':
                modifySeattleRainfall(conn)
            elif functions == '0':
                print("The program is now closing")
                closeConnection(conn, database)

if __name__ == '__main__':
    main()