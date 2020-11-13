/* Created this file to test the queries and make sure they work correctly */ 

--Table containing all of the data, from 1948 to 2017
CREATE TABLE IF NOT EXISTS SeattleRainfall (
    DATE DATE NOT NULL, 
    PRPC REAL NOT NULL, 
    TMAX INT NOT NULL, 
    TMIN INT NOT NULL, 
    RAIN CHAR NOT NULL
)

--Table containing average data from any given year, indicated by the user
CREATE TABLE IF NOT EXISTS AnnualReport (
    ar_year     INT, 
    ar_avgPrcp     REAL, 
    ar_avgTemp  REAL, 
    ar_numRainDays INT
)

--A year's data broken down into months, year given by the user
CREATE TABLE IF NOT EXISTS MonthlyReport (
    mr_monthYear DATE, 
    mr_avgPrcp  REAL,
    mr_avgTemp  REAL,
    mr_numRainDays INT
)

--Daily report from a given month
CREATE TABLE IF NOT EXISTS DailyReport (
    dr_date DATE NOT NULL, 
    dr_prpc REAL NOT NULL,
    dr_tmax INT NOT NULL,
    dr_tmin INT NOT NULL, 
    dr_rain CHAR NOT NULL
)

--Report from a given range of dates
CREATE TABLE IF NOT EXISTS RangedReport (
    rr_startDate DATE, 
    rr_endDate  DATE, 
    rr_avgPrpc  REAL NOT NULL, 
    rr_avgTemp  REAL NOT NULL,
    rr_numRainDays  INT NOT NULL,
    rr_totalDays INT NOT NULL
)

--Query to get an annual report. 
INSERT INTO AnnualReport (ar_avgPrcp, ar_avgTemp, ar_numRainDays)
SELECT AVG(PRCP), (AVG(TMAX)+AVG(TMIN))/2, (
    SELECT COUNT(RAIN)
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE' AND strftime('%Y', DATE) = '1996'
) rainn
FROM SeattleRainfall
WHERE strftime('%Y', DATE) = '1996'

--Query to get a monthly report
INSERT INTO MonthlyReport (mr_monthYear, mr_avgPrcp, mr_avgTemp)
SELECT strftime('%m-%Y', DATE), AVG(PRCP), (AVG(TMAX)+AVG(TMIN))/2 as temp
/* (
    SELECT COUNT(RAIN)
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE' AND strftime('%Y', DATE) = '1948'
    GROUP BY strftime('%m', DATE)
) rainDays */
FROM SeattleRainfall
WHERE strftime('%Y', DATE) = '1948'
GROUP BY strftime('%m', DATE)

--Query to get a daily report from a specified month
INSERT INTO DailyReport
SELECT *
FROM SeattleRainfall
WHERE DATE >= "1996-01-01" AND DATE <= "1996-01-31"
GROUP BY strftime('%d', DATE) 

--Query to get a ranged report (specified start and end dates)
INSERT INTO RangedReport (rr_avgPrpc, rr_avgTemp, rr_numRainDays, rr_totalDays)
SELECT AVG(PRCP), (AVG(TMAX)+AVG(TMIN))/2, (
    SELECT COUNT(RAIN)
    FROM SeattleRainfall
    WHERE RAIN = 'TRUE' AND (DATE >= "1980-10-13" AND DATE <= "1985-03-25")
) rainn, COUNT(DATE)
FROM SeattleRainfall
WHERE DATE >= "1980-10-13" AND DATE <= "1985-03-25"