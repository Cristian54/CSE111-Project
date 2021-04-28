from flask import Flask, render_template, url_for, request
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Data/database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#db.Model.metadata.reflect(db.engine)

class Rain(db.Model):
    __tablename__ = 'SeattleRainfall'
    __table_args__ = { 'extend_existing': True }
    DATE = db.Column(db.Date, primary_key=True) 
    PRCP = db.Column(db.Float)
    TMAX = db.Column(db.Integer) 
    TMIN = db.Column(db.Integer)  
    RAIN = db.Column(db.Boolean)
        
@app.route('/')
def home_page():
    days = Rain.query.count()
    return render_template('home.html', days = days)

@app.route('/dailyReport', methods = ['POST', 'GET'])
def dailyReport():
    if request.method == 'GET':
        return f"The URL /dailyReport is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form = request.form
        yearMonth = form.get('Year') + "-" + form.get('Month')
        report = Rain.query.filter(Rain.DATE.startswith(yearMonth)).all()
        return render_template('DailyReport.html', dailyReport = report, yearMonth = yearMonth)

@app.route('/annualReport', methods = ['POST', 'GET'])
def annualReport():
    if request.method == 'GET':
        return f"The URL /annualReport is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        formData = request.form
        year = formData.get('Year')
        
        numRainyDays = Rain.query.filter(Rain.DATE.startswith(year), Rain.RAIN == 'TRUE').count()
        avgPrcp = round(db.session.query(db.func.avg(Rain.PRCP)).filter(Rain.DATE.startswith(year), Rain.RAIN == 'TRUE').scalar(), 3)
        avgMaxTemp = round(db.session.query(db.func.avg(Rain.TMAX)).filter(Rain.DATE.startswith(year)).scalar())
        avgMinTemp = round(db.session.query(db.func.avg(Rain.TMIN)).filter(Rain.DATE.startswith(year)).scalar())
        
        return render_template('AnnualReport.html', year = year, rain = numRainyDays, avgPrcp = avgPrcp, avgMaxTemp = avgMaxTemp, avgMinTemp = avgMinTemp)

@app.route('/monthlyReport', methods = ['POST', 'GET'])
def monthlyReport():
    if request.method == 'GET':
        return f"The URL /monthlyReport is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        formData = request.form
        year = formData.get('Year')
        
        monthAvgTemp = db.session.query(db.func.strftime('%m-%Y', Rain.DATE), db.func.avg(Rain.TMAX), db.func.avg(Rain.TMIN)).filter(Rain.DATE.startswith(year)).group_by(db.func.strftime('%m', Rain.DATE)).all()
        avgPrcp = db.session.query(db.func.avg(Rain.PRCP)).filter(Rain.DATE.startswith(year), Rain.RAIN == 'TRUE').group_by(db.func.strftime('%m', Rain.DATE)).all()
        numRainyDays = db.session.query(db.func.count(Rain.RAIN)).filter(Rain.DATE.startswith(year), Rain.RAIN == 'TRUE').group_by(db.func.strftime('%m', Rain.DATE)).all()
         
        return render_template('MonthlyReport.html', year = year, monthTemp = monthAvgTemp, avgPrcp = avgPrcp, rainDays = numRainyDays)
     
@app.route('/RangedReport', methods = ['POST', 'GET'])  
def RangedReport():
    if request.method == 'GET':
        return f"The URL /RangedReport is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        formData = request.form
        start = formData.get('start')
        end = formData.get('end')
        
        totDays = db.session.query(db.func.count()).filter(Rain.DATE >= start, Rain.DATE <= end).scalar()
        rainPrcp = db.session.query(db.func.count(), db.func.avg(Rain.PRCP)).filter(Rain.DATE >= start, Rain.DATE <= end, Rain.RAIN == 'TRUE')
        hottest = db.session.query(db.func.strftime('%m-%d-%Y', Rain.DATE), db.func.max(Rain.TMAX)).filter(Rain.DATE >= start, Rain.DATE <= end).all()
        coldest = db.session.query(db.func.strftime('%m-%d-%Y', Rain.DATE), db.func.min(Rain.TMIN)).filter(Rain.DATE >= start, Rain.DATE <= end).all()
        topPrcp = db.session.query(db.func.strftime('%m-%d-%Y', Rain.DATE), db.func.max(Rain.PRCP)).filter(Rain.DATE >= start, Rain.DATE <= end).all()
        
        return render_template('RangedReport.html', start = start, end = end, days = totDays, rain = rainPrcp, hotDay = hottest, coldDay = coldest, prcp = topPrcp)   

@app.route('/OneDay', methods = ['POST', 'GET'])
def OneDay():
    if request.method == 'GET':
        return f"The URL /OneDay is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        formData = request.form
        day = formData.get('day')
        days = Rain.query.filter(Rain.DATE.endswith(day)).all()
        return render_template('OneDay.html', day = day, days = days)

@app.route('/lmRain', methods = ['POST', 'GET'])
def lmRain():
    if request.method == 'GET':
        return f"The URL /OneDay is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        formData = request.form
        choice = formData.get('listChoice')
        
        if choice == 'M':
            yearList = db.session.query(db.func.strftime('%Y', Rain.DATE), db.func.count(Rain.RAIN)).filter(Rain.RAIN == 'TRUE').group_by(db.func.strftime('%Y', Rain.DATE)).order_by(db.func.count(Rain.RAIN).desc()).all()
            choice = 'most'
            return render_template('lmRain.html', choice = choice, years = yearList)
        elif choice == 'L':
            yearList = db.session.query(db.func.strftime('%Y', Rain.DATE), db.func.count(Rain.RAIN)).filter(Rain.RAIN == 'TRUE').group_by(db.func.strftime('%Y', Rain.DATE)).order_by(db.func.count(Rain.RAIN).asc()).all()
            choice = 'least'
            return render_template('lmRain.html', choice = choice, years = yearList)
        
if __name__ == "__main__":
    app.run(debug=True)