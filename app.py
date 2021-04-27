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
    #oneMonth = Rain.query.filter(Rain.DATE.startswith('1948-01')).all()
    
    #for day in oneMonth:
        #print("Date: ", day.DATE, "Max Temp: ", day.TMAX)
         
    return render_template('home.html', days = days)


@app.route('/monthlyReport', methods = ['POST', 'GET'])
def monthlyReport():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form = request.form
        yearMonth = form.get('Year') + "-" + form.get('Month')
        report = Rain.query.filter(Rain.DATE.startswith(yearMonth)).all()
        return render_template('monthlyReport.html', monthlyReport = report, yearMonth = yearMonth)

if __name__ == "__main__":
    app.run(debug=True)