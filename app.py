from flask import Flask, render_template, url_for, request, g
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
    PRCP = db.Column(db.Numeric)
    TMAX = db.Column(db.Integer) 
    TMIN = db.Column(db.Integer)  
    RAIN = db.Column(db.Boolean)
        

@app.route('/')
def home_page():
    days = Rain.query.count()
    hotDays = Rain.query.filter_by(TMAX = 98).all()
    
    for hd in hotDays:
        print("Date: ", hd.DATE, " Temp: ", hd.TMAX)
         
    return render_template('home.html', days = days, hotDays = hotDays)


'''
@app.route('/listReport', methods = ['GET', 'POST'])
def listReport():
    if request.method == 'GET':
        year = request.form["year"]
        month = request.form["month"]
        date = year + "-" + month
    
        sql = """
        SELECT *
        FROM SeattleRainfall
        WHERE strftime('%Y-%m', DATE) = ?
        GROUP BY strftime('%d', DATE) """
    
        cur = get_db().cursor()
        cur.execute(sql, (date,))
        report = cur.fetchall()
        #rows = getDailyReport(conn, year, month)
        cur.close()
        
        for row in report:
            if row[4] == 'TRUE':
                rain = 'Rained'
            else:
                rain = 'Did not rain'
            print("Date:", row[0], "|", rain, "| Precipitation:", row[1], "| Highest/Lowest temperature (F):", row[2], "/", row[3])
        
        
        return render_template('list.html', rows = report)
    else:
        print("this isn't a post request")
    '''

if __name__ == "__main__":
    app.run(debug=True)