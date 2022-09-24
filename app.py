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
    event = db.Column(db.String(200),nullable=False)
    eventDate = db.Column(db.Date ,nullable = False)
    eventTime =  db.Column(db.Time ,nullable = False)
    eventEndDate = db.Column(db.Date ,nullable = False)
    eventEndTime =  db.Column(db.Time ,nullable = False)
    deptName = db.Column(db.String(40),nullable = False)
    isApproved = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.name

@app.route("/")
@app.route("/dashboard")
def getCanteenPerson():
    if request.method == "POST":
        pass

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
    
    #first upcoming event
    upcoming_event = dict()
    events = Event.query.all()
    if len(events) != 0:
        up_event = Event.query.filter_by(isApproved=True).order_by(Event.eventDate.asc()).order_by(Event.eventTime.asc())[0]
        upcoming_event['name'] = up_event.name
        upcoming_event['event'] = up_event.event
        upcoming_event['department_name'] = up_event.deptName
        upcoming_event['event_date'] = str(up_event.eventDate)
        upcoming_event['event_time'] = str(up_event.eventTime)
        upcoming_event['event_end_date'] = str(up_event.eventEndDate)
        upcoming_event['event_end_time'] = str(up_event.eventEndTime)

    # all upcoming event
    response_list = []
    dateTimeList = []
    sorted_events = Event.query.filter_by(isApproved=True).order_by(Event.eventDate.asc()).order_by(Event.eventTime.asc())
    for j in sorted_events:
        response_dict = dict()
        response_dict['name'] = j.name
        response_dict['event'] = j.event
        response_dict['department_name'] = j.deptName
        response_dict['event_date'] = str(j.eventDate)
        response_dict['event_time'] = str(j.eventTime)
        response_dict['event_end_date'] = str(j.eventEndDate)
        response_dict['event_end_time'] = str(j.eventEndTime)
        response_list.append(response_dict)

    return render_template("index.html", count = count, total_seats = total_seats, available_seats = available, inside_canteen = res, upcoming_event = upcoming_event, response_list=response_list)


@app.route("/add-event", methods=["POST"])
def addevent():
    name = request.form['name']
    eventName = request.form['event']
    deptName = request.form['dept_name']
    eventDate = datetime.strptime(request.form['date'],"%d-%m-%Y").date()
    eventTime = datetime.strptime(request.form['time'],"%H:%M").time()
    eventEndDate = datetime.strptime(request.form['end_date'],"%d-%m-%Y").date()
    eventEndTime = datetime.strptime(request.form['end_time'],"%H:%M").time()
    events = Event.query.all()
    for event in events:
        if event.eventDate == eventDate and eventTime >= event.eventTime and eventEndTime <= event.eventEndTime:
            return jsonify({"message":"Time slots has been occupied, Please choose another time :("})
        if event.eventDate == eventDate and eventTime < event.eventTime and eventEndTime > event.eventEndTime:
            return jsonify({"message":"Time slots has been occupied, Please choose another time :("})
        if event.eventDate == eventDate and event.eventEndTime > eventTime and event.eventEndTime < eventEndTime:
            return jsonify({"message":"Time slots has been occupied, Please choose another time :("})
        if event.eventDate == eventDate and eventTime < event.eventTime and eventTime < event.eventEndTime:
            return jsonify({"message":"Time slots has been occupied, Please choose another time :("})
    if eventDate > eventEndDate:
        return jsonify({"message":"Invalid Date :("})
    if eventDate == datetime.now().date():
        if eventTime > eventEndTime:
            return jsonify({"message":"Invalid Date :("})
    if eventDate < datetime.now().date():
        return jsonify({"message":"Please choose future datetime :("})
    if eventDate == datetime.now().date() and eventTime < datetime.now().time():
        return jsonify({"message":"Please choose future datetime :("})

    db.session.add(Event(name=name, event=eventName, deptName=deptName, eventTime=eventTime, eventDate=eventDate, eventEndDate=eventEndDate, eventEndTime=eventEndTime, isApproved=True))
    db.session.commit()
    return jsonify({"message": "Event added successfully!"})

@app.route('/upcoming-events', methods=["GET"])
def upcoming_events():
    response_list = []
    dateTimeList = []
    sorted_events = Event.query.filter_by(isApproved=True).order_by(Event.eventDate.asc()).order_by(Event.eventTime.asc())
    for j in sorted_events:
        response_dict = dict()
        response_dict['name'] = j.name
        response_dict['event'] = j.event
        response_dict['department_name'] = j.deptName
        response_dict['event_date'] = str(j.eventDate)
        response_dict['event_time'] = str(j.eventTime)
        response_dict['event_end_date'] = str(j.eventEndDate)
        response_dict['event_end_time'] = str(j.eventEndTime)
        response_list.append(response_dict)
    return jsonify({'message':response_list})

@app.route('/approve-event/<id>', methods=["PUT"])
def approve_event(id):
    event = Event.query.filter_by(sno=id).all()
    if len(event) != 0:
        if request.form['isApproved'] == True:
            event[0].isApproved = True
            db.session.commit()
            return jsonify({"message":"Updated successfully :)"})
        else:
            event[0].isApproved = False
            db.session.commit()
            return jsonify({"message":"Updated successfully :)"})
    else:
        return jsonify({"message":"Invalid ID :("})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)