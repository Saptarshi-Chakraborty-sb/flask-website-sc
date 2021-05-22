import email
from os import name
from flask import Flask, render_template, request, session,redirect
from flask.signals import message_flashed
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask_mail import Mail, Message
import json


with open('saptarshi.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key='Saptarshi-secret-key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=456,
    MAIL_USE_SSL='True',
    MAIL_USERNAME=params['email-user'],
    MAIL_PASSWORD=params['email-password']
)
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = params['database_uri']
db = SQLAlchemy(app)
# Note: If "No Module named MySQldb" error comes, run "pip install mysqlclient" in Windows Powershell Admin


class Contacts(db.Model):
    sno = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, primary_key=False)
    phone_num = db.Column(db.Integer, nullable=True, primary_key=False)
    email = db.Column(db.String(50), nullable=False, primary_key=False)
    msg = db.Column(db.String(150), nullable=False, primary_key=False)
    date = db.Column(db.String(17), nullable=True, primary_key=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(50), nullable=False, primary_key=False)
    slug = db.Column(db.String(30), nullable=False, primary_key=False)
    dn_link = db.Column(db.String(100), nullable=False, primary_key=False)
    img_link = db.Column(db.String(30), nullable=False, primary_key=False)
    details = db.Column(db.String(500), nullable=False, primary_key=False)
    date = db.Column(db.String(17), nullable=True, primary_key=False)


# ~~~~ Home Page ~~~~
@app.route("/")
def home_route():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)


# ~~~~ Contact Page ~~~~
@app.route("/contact", methods=['GET', 'POST'])
def contact_route():
    if(request.method == 'POST'):
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')
# Push to Database
        entry = Contacts(name=name, email=email, phone_num=phone,
                         msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        # mail.send_message('New Response in Website, form '+ name,
        #           sender=name,
        #           recipients=[params['email-user']],
        #           body="New Responce form Contacts"+"\n" + "Name : " + name + "\n" + "Email : " + email + "\n" + "Message : " + message
        #           )
    return render_template('contact.html', params=params)


# ~~~~ Log In Page ~~~~~
@app.route("/login", methods=['GET', 'POST'])
def login_route():
    if ('user' in session  and session['user'] == params['admin_username']):
        return render_template('dashboard.html')

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('passw')
        if (username == params['admin_username'] and userpass == params['admin_password']):
            session['user'] = username
            return render_template('dashboard.html')
        else:
            return render_template('index.html')
    else:
        return render_template('login.html', params=params)


# ~~~~ Log Out ~~~~
@app.route('/logout')
def logout_route():
    session.pop('user')
    return redirect('/login')


# ~~~~ Posts Page ~~~~
@app.route("/post/<string:post_slug>", methods=['GET'])
def posts_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=post)

# ~~~~ Dashboard Page ~~~~


@app.route("/dashboard_FtIux7tirSsmzYYkPLrcY")
def dashboard_route():
    return render_template('dashboard.html', params=params)


app.run(debug=True)
