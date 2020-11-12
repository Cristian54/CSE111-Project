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
    mr_year INT NOT NULL, 
    mr_month INT NOT NULL, 
    mr_avgPrcp  REAL NOT NULL,
    mr_avgTemp  REAL NOT NULL,
    mr_numRainDays INT NOT NULL
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
    rr_startDate DATE NOT NULL, 
    rr_endDate  DATE NOT NULL, 
    rr_avgPrpc  REAL NOT NULL, 
    rr_avgTemp  REAL NOT NULL,
    rr_numRainDays  INT NOT NULL
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



