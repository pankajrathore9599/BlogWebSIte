from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail
from datetime import datetime
import json

# configuru=ing prams (config.json) for local and production server with file handling
with open('templates/config.json','r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
# setting secret key for session handling
app.secret_key = 'super-secret-key'
# sending information of contact page on my email
# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME =  params['gmail_user'],
#     MAIL_PASSWORD = params['gmail_password']
# )
# mail = Mail(app)


# 'mysql://username:password@localhost/db_name' (sqlalchemy uri)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

# database app
db = SQLAlchemy(app)

# Making class for contact tabel in database for calling data from it.
class Contacts(db.Model):
    # data in db table (SN, Name, Email, Phone_num, Message, Date)
    SN = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(20), nullable=False)
    Phone_num = db.Column(db.String(12), nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)

# Making class for post tabel in database fot calling data from it.
class Posts(db.Model):
    # data in db table (SN, Title, Slug, Content, Date)
    SN = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    SubTitle = db.Column(db.String(50), nullable=False)
    Slug = db.Column(db.String(20), nullable=False)
    Content = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    Img_file = db.Column(db.String(12), nullable=True)


# route for homepage
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)

# route for about page
@app.route("/about")
def about():
    return render_template('about.html', params=params)

# route for post page and rendering the post from the user.
@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(Slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

# route of contact page
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method=='POST'):
        #Add entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(Name=name, Phone_num=phone, Email=email, Message=message, Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New Message From Blog', 
        #                     sender='email', 
        #                     recipients= [params['gmail_user']],
        #                     body = message + "\n" + phone
        #                     )

    return render_template('contact.html', params=params)
 
# route of dashboard
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # this is for if user is already login
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params, posts=posts)

    # this is for when 
    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params, posts=posts)
    
    else:
        return render_template('login.html', params=params)

# route for editing posts
@app.route("/edit/<string:SN>", methods = ['GET', 'POST'])
def editpost(SN):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            content = request.form.get('content')
            image = request.form.get('image')
            date = datetime.now()

            if SN=='0':
                post = Posts(Title = box_title, SubTitle = subtitle, Slug = slug, Content = content, Date=date, Img_file = image)
                db.session.add(post)
                db.session.commit

        return render_template('edit.html', params=params, SN=SN)



                
app.run(debug=True)