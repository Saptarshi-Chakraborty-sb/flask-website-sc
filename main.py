from operator import pos
import math
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
import json

with open('saptarshi.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = 'Saptarshi-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
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
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))

    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)

    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]

    if(page==1):
        prev="#"
        next="/?page=" + str(page + 1)

    elif(page==last):
        prev="/?page=" + str(page - 1)
        next="#"

    else:
        prev="/?page=" + str(page - 1)
        next="/?page=" + str(page + 1)
        

    return render_template('index.html', params=params, posts=posts,prev=prev, next=next)


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
    if 'user' in session and session['user'] == params['admin_username']    :
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params,posts=posts)

    if request.method == "POST":
        username = request.form.get('uname')
        userpass = request.form.get('passw')
        if (username == params['admin_username'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', posts=posts)
        else:
            return render_template('login.html')
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


# ~~~~ Edit Page ~~~~
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit_route(sno):
    if ('user' in session and session['user'] == params['admin_username']):
        if(request.method) == "POST":
            got_title = request.form.get('ftitle')
            got_slug = request.form.get('fslug')
            got_download = request.form.get('fdownload')
            got_image = request.form.get('fimage')
            got_details = request.form.get('fdetails')  
            got_date = datetime.now()

            if sno == '0':
                post = Posts(title=got_title, slug=got_slug,dn_link=got_download,img_link=got_image,details=got_details,date=got_date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=got_title
                post.slug=got_slug
                post.dn_link=got_download
                post.img_link=got_image
                post.details=got_details
                post.date=got_date
                db.session.commit()
                return redirect('/login')
 
    post=Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params,post=post,sno=sno)


# ~~~~ Delete Post ~~~~
@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete_route(sno):
    if ('user' in session and session['user'] == params['admin_username']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()

        return redirect('/login')
    else:
        return redirect('/login')




# ~~~~ File Uploader ~~~~
@app.route("/uploader", methods=['GET','POST'])
def upload_route():
    if ('user' in session and session['user'] == params['admin_username']):
        if(request.method) == "POST":
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return redirect('/login')


# ~~~~ None Page ~~~~
@app.route("/none")
def none():
    return "None is Here"

app.run(debug=True)
