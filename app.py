import json
from flask import Flask, render_template, jsonify, request
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

class Event(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date ,nullable = False)
    event_time =  db.Column(db.Time ,nullable = False)
    department_name = db.Column(db.String(40),nullable = False)

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

@app.route("/add-event", methods=["GET", "POST"])
def addevent():
    name = request.form['name']
    event_time = datetime.strptime(request.form['time'],"%H:%M").time()
    event_date = datetime.strptime(request.form['date'],"%Y-%m-%d").date()
    department = request.form['department']
    db.session.add(Event(name=name, event_time=event_time, event_date=event_date, department_name=department))
    db.session.commit()
    return jsonify({"message": f"Event added successfully on {event_date} at {event_time}"})

@app.route('/upcoming-events')
def upcoming_events():
    list = []
    all_data = Event.query.all()
    test_list = []
    for i in all_data:
        date_and_time = datetime.combine(i.event_date, i.event_time)
        test_list.append(date_and_time)
    
    print(test_list)
    
    for i in range(len(test_list)):
        data = Event.query.filter_by(event_date=(sorted(test_list))[i]).all()
        for j in data:
            dict = {}
            dict['name'] = j.name
            dict['event_time'] = j.event_date
            dict['department_name'] = j.department_name
            list.append(dict)
    return jsonify({'message':list})

if __name__ == '__main__':
    app.run(debug=True)