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
    #hotDays = Rain.query.filter_by(TMAX = 98).all()
         
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
        
if __name__ == "__main__":
    app.run(debug=True)