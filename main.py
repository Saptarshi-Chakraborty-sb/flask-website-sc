from flask import Flask, render_template, request
from flask.signals import message_flashed
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


with open('saptarshi.json','r') as c:
    params = json.load(c) ["params"]
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = params['database_uri']
db = SQLAlchemy(app)
# Note: If "No Module named MySQldb" error comes run "pip install mysqlclient" in Windows Powershell Admin


class Contacts(db.Model):
    sno = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, primary_key=False)
    phone_num = db.Column(db.Integer, nullable=True, primary_key=False)
    email = db.Column(db.String(50), nullable=False, primary_key=False)
    msg = db.Column(db.String(150), nullable=False, primary_key=False)
    date = db.Column(db.String(17), nullable=True, primary_key=False)


# Home Page
@app.route("/")
def home():
    return render_template('index.html')


# Contact Page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')

        entry = Contacts(name=name, email=email, phone_num=phone, msg=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


# Log In Page
@app.route("/login")
def login():
    return render_template('login.html')


# Posts Page
@app.route("/post")
def posts():
    return render_template('post.html')

# Dashboard Page


@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


app.run(debug=True)
