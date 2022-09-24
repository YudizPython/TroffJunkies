import json
from flask import Flask, render_template, jsonify
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///canteen.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Canteen(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    time = db.Column(db.DateTime)
    estTime = db.Column(db.DateTime)

    def __str__(self):
        return self.name

@app.route("/count")
def Count():
    # api to count of persons in canteen
    count = pd.read_csv('insideCanteen.csv')
    count = len(count)
    total_seats = 42
    available = total_seats - count
    return jsonify({"count": count, "total_seats": total_seats, "available": available})

@app.route("/get-canteen-person")
def getCanteenPerson():
    persons = pd.read_csv("insideCanteen.csv")
    names = list(persons["Name"])
    time = list(persons["Time"])
    EstTime = list(persons["EstTime"])

    res = []
    for i in range(len(names)):
        curr = {}
        curr["Name"] = names[i]
        curr["Time"] = time[i]
        curr["EstTime"] = EstTime[i]
        res.append(curr)

    return jsonify({"inside_canteen": res})

@app.route("/inside-canteen")
def insideCanteen():
    pass

if __name__ == '__main__':
    app.run(debug=True)


########################################################################################################
import json
from flask import Flask, render_template, jsonify, request
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///canteen.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)

class Canteen(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    time = db.Column(db.DateTime)
    estTime = db.Column(db.DateTime)

    def __str__(self):
        return self.name

class Event(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date ,nullable = False)
    time =  db.Column(db.Time ,nullable = False)
    deptName = db.Column(db.String(40),nullable = False)

    def __str__(self):
        return self.name

@app.route("/count")
def Count():
    # api to count of persons in canteen
    count = pd.read_csv('insideCanteen.csv')
    count = len(count)
    total_seats = 42
    available = total_seats - count
    return jsonify({"count": count, "total_seats": total_seats, "available": available})

@app.route("/dashboard")
def getCanteenPerson():
    persons = pd.read_csv("insideCanteen.csv")

    # count of persons in canteen
    count = len(persons)
    total_seats = 42
    available = total_seats - count

    names = list(persons["Name"])
    time = list(persons["Time"])
    EstTime = list(persons["EstTime"])

    res = []
    for i in range(len(names)):
        curr = {}
        curr["Name"] = names[i]
        curr["Time"] = time[i]
        curr["EstTime"] = EstTime[i]
        res.append(curr)

    return jsonify({"count": count, "total_seats": total_seats, "available_seats": available, "inside_canteen": res})

@app.route("/inside-canteen")
def insideCanteen():
    pass

@app.route("/add-event", methods=["POST"])
def addevent():
    name = request.form['name']
    time = datetime.strptime(request.form['time'],"%H:%M").time()
    date = datetime.strptime(request.form['date'],"%Y-%m-%d").date()
    department = request.form['department']
    db.session.add(Event(name=name, time=time, date=date, deptName=department))
    db.session.commit()
    return jsonify({"message": f"Event added successfully on {date} at {time}"})

@app.route('/Event_Check',methods=['GET'])
def Event_Check():
    list = []
    all_data = Event.query.all()
    test_list = []
    for i in all_data:
        date_and_time = datetime.combine(i.date,i.time)
        test_list.append(date_and_time)
    for i in range(0,len(test_list)):
        data = Event.query.filter_by(date=((sorted(test_list))[i]).date()).filter_by(time=((sorted(test_list))[i]).time()).all()
        for j in data:
            dict = {}
            dict['name'] = j.name
            dict['date'] = str(j.date)
            dict['time'] = str(j.time)
            dict['deptName'] = j.deptName
            list.append(dict)
    return jsonify({'message':list})

if _name_ == '__main__':
    app.run(debug=True)