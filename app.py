########################################################################################################
import json
from flask import Flask, render_template, jsonify, request
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import *
from flask_mail import *
from werkzeug.security import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///canteen.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)

##################################################
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = '',
    MAIL_PASSWORD = '',
))
mail = Mail(app)
###################################################

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
    end_time = db.Column(db.Time,nullable=False)
    deptName = db.Column(db.String(40),nullable = False)

    def __str__(self):
        return self.name
    
class Admin(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(50),nullable=True)
    password = db.Column(db.String(50),nullable=True)


##########################################################

@app.route("/count")
def Count():
    # api to count of persons in canteen
    count = pd.read_csv('insideCanteen.csv')
    count = len(count)
    total_seats = 42
    available = total_seats - count
    return jsonify({"count": count, "total_seats": total_seats, "available": available})

@app.route('/register',methods=['POST'])
def Register():
    all_data = request.get_json()
    db.session.add(Admin(user_name=all_data['user_name'],email=all_data['email'],password=all_data['password']))
    db.session.commit()
    return jsonify({"Message":"Data add successfully!!"})

@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user_id = Admin.query.filter_by(email=email).first()
    if check_password_hash(user_id.password,password):
        return jsonify({'Successfully':'Loggin Successfully!!'})
    return jsonify({'message':'Password not match!!'})

@app.route('/forgot_password',methods=['POST'])
def forgot_password():  
    if request.json['email']:
        id = Admin.query.filter_by(email = request.json['email']).first().id
        msg = Message('Hello',sender="",recipients=[request.json['email']])
        msg.body = f"Link to change password http://127.0.0.1:5000/change_password/{id}"
        mail.send(msg)
        return jsonify({'message':"successfully!!"})
    return jsonify({'message':"unsuccessfully!!"})
 
@app.route('/change_password/<int:id>',methods=['POST'])
def change_password(id):
    new_password = request.json['new_password']
    confirm_password = request.json['confirm_password']
    geting_user = Admin.query.filter_by(id = id).first()
    if new_password==confirm_password:
        hash_password = generate_password_hash(new_password)
        geting_user.password = hash_password
        db.session.commit()
        return jsonify({'message':'password change succesfully!!'})
    return jsonify({'message':'new_password and old_password not match!!'})

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
    end_time = datetime.strptime(request.form['end_time'],"%H:%M").time()
    date = datetime.strptime(request.form['date'],"%Y-%m-%d").date()
    department = request.form['department']
    all_data = Event.query.all()
    for i in all_data:
        if (i.time <= time <= i.end_time) and (i.time <= end_time <= i.end_time) and date==i.date:  
            return jsonify({'message':'Sorry time is full!!'})
    db.session.add(Event(name=name, time=time, date=date,end_time=end_time, deptName=department))
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

if __name__ == '__main__':
    app.run(debug=True)