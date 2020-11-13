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
) rainDays, COUNT(DATE)
FROM SeattleRainfall
WHERE DATE >= "1980-10-13" AND DATE <= "1985-03-25"

--Query to only get the number of rainy days from a week, month, year or any other period of time
SELECT COUNT(RAIN)
FROM SeattleRainfall
WHERE RAIN = 'TRUE' AND DATE >= "2000-01-01" AND DATE <= "2010-12-31"

--Find the year with the most rainy days 
--Alternative query: list all years by the amount of rainy days they had (remove limit)
SELECT strftime('%Y', DATE), COUNT(RAIN)
FROM SeattleRainfall
WHERE RAIN = 'TRUE'
GROUP BY strftime('%Y', DATE)
ORDER BY COUNT(RAIN) DESC
LIMIT 1 

--Find the year with the least rainy days
SELECT strftime('%Y', DATE), COUNT(RAIN)
FROM SeattleRainfall
WHERE RAIN = 'TRUE'
GROUP BY strftime('%Y', DATE)
ORDER BY COUNT(RAIN) ASC
LIMIT 1 

--List the coldest day(s), optionally only looking at rainy days or days without rain. 
--Can also add another condition to find the coldest day with the least/highest amount of precipitation 
SELECT DATE, MIN(TMIN)
FROM SeattleRainfall
--WHERE RAIN = 'FALSE'  
GROUP BY strftime('%d', DATE) 
ORDER BY MIN(TMIN) ASC
LIMIT 10

--List the hottest day(s)
SELECT DATE, MAX(TMAX)
FROM SeattleRainfall
--WHERE RAIN = 'FALSE'
GROUP BY strftime('%d', DATE) 
ORDER BY MAX(TMAX) DESC
LIMIT 10

--List the hottest and coldest day from every month in a specified year 
SELECT strftime('%m-%Y', DATE), MAX(TMAX), MIN(TMIN)
FROM SeattleRainfall
WHERE strftime('%Y', DATE) = '1999'
GROUP BY strftime('%m', DATE)





-- data of when rain is present for the day
select * 
from SeattleRainfall
where RAIN = 'TRUE'

-- data in seattle where data ranges from 2000-latest data
select *
from SeattleRainfall
where DATE > '2000-%-%'
order by DATE DESC

-- reporting days where it rained but temperature was relatively average for seattle
    --source https://www.tripsavvy.com/does-it-really-rain-in-seattle-4159184#:~:text=On%20average%2C%20Seattle%20gets%2038,time%2C%20depending%20on%20the%20season.
select distinct DATE, TMAX, TMIN, RAIN
from SeattleRainfall
WHERE RAIN = 'TRUE' AND
TMAX >= '70' AND
TMIN >= '40'
order by DATE

-- what is current number of data entry within the database
select count(*)
from SeattleRainfall

-- average max and min temp within 20 years from 1990 to 2010
select avg(TMAX), avg(TMIN)
from SeattleRainfall
where DATE < '2010-12-31' AND
DATE > '1990-1-1'

-- shows the data within last year,since last data ended 2017-12-14, it will be in year 2017
select *
from SeattleRainfall
where DATE < '2017-12-14' AND
DATE > '2017-1-1'
order by DATE DESC

-- look for day(s) where seattle had 0 degree or less even though it did not rain
select *
from SeattleRainfall
where TMIN <=  '0' AND
rain = 'FALSE'

-- showing count where there is rain and no rain
select count(rain1) as rained, count(rain2) as noRain
from (
    select 
    case when rain = 'TRUE' then rain end as rain1,
    case when rain = 'FALSE' then rain end as rain2
    from SeattleRainfall
) as x

--  insert query adding data into SeattleRainfall
insert into SeattleRainfall ('DATE', 'PRCP', 'TMAX', 'TMIN', 'RAIN') VALUES
('2020-11-11', '0', '46', '40', 'FALSE')

-- update query on info from above
update SeattleRainfall
SET RAIN = 'TRUE'
where DATE = '2020-11-11'

-- delete query (delete above)
delete 
from SeattleRainfall
where DATE = '2020-11-11'