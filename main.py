from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import json
import math

with open('config.json','r') as file:
    params = json.load(file)['params']

app  =Flask(__name__,template_folder='template')
app.secret_key="12@gdj7"

if params['local_server']:
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']=params['prod_uri']

db= SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer,primary_key=True,default=0)
    name = db.Column(db.String(20),nullable=False)
    phone_no = db.Column(db.String(12),nullable=False)
    mes = db.Column(db.String(100),nullable=False)
    date = db.Column(db.String(12),nullable=False)
    email = db.Column(db.String(20),nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True,default=0)
    title = db.Column(db.String(20),nullable=False)
    subtitle = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(100),nullable=False)
    slug = db.Column(db.String(100),nullable=False)
    author = db.Column(db.String(20),nullable=False)
    date = db.Column(db.String(20),nullable=False)
    img_url = db.Column(db.String(50),nullable=False)

@app.route('/')
def home():
    page_no = request.args.get('page_no')
    posts = Posts.query.filter_by().all()
    posts.reverse()
    last = math.floor(len(posts)/params['post_per_page'])

    if page_no is None:
        page_no = 0
    else:
        page_no = int(page_no)

    if page_no==0:
        next = str(page_no+1)
        prev = "#"
    elif page_no==last:
        next = "#"
        prev = str(page_no-1)
    else:
        next = str(page_no+1)
        prev = str(page_no-1)

    rlim = (page_no+1)*params['post_per_page']
    llim = rlim-params['post_per_page']
    posts = posts[llim:rlim]
    return render_template('index.html',params=params,posts=posts,prev=prev,next=next,isLoggedIn = (True if 'user' in session else False))

@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' in session and session['user']==params['admin_username'] :
        posts = Posts.query.all()
        return render_template("dashboard.html",params=params,posts=posts,isLoggedIn = (True if 'user' in session else False))

    if request.method=='POST':
        uname = request.form.get('uname')
        password = request.form.get('pass')
        if uname==params['admin_username'] and password==params['admin_userpass'] :
            session['user'] = uname
            posts = Posts.query.all()
            return render_template("dashboard.html",params=params,posts=posts,isLoggedIn = (True if 'user' in session else False))

    return render_template("login.html",params=params)


@app.route('/contact',methods = ['GET','POST'])
def contact():
    giveResponse = False;
    if request.method=='POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phno')
        message = request.form.get('message')

        entry = Contact(name=name,phone_no=phone_no,mes=message,date=datetime.now(),email=email)

        db.session.add(entry)
        db.session.commit()
        giveResponse=True


    return render_template('contact.html',giveResponse=giveResponse,params=params,isLoggedIn = (True if 'user' in session else False))

@app.route('/post/<string:post_slug>',methods=['GET'])
def Post(post_slug):
    Req_Post = Posts.query.filter_by(slug = post_slug).first()

    return render_template('post.html',post=Req_Post,params=params,isLoggedIn = (True if 'user' in session else False))

@app.route('/about')
def about():
    return render_template('about.html',params=params,isLoggedIn = (True if 'user' in session else False))

@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_username'] :
        if request.method=='POST' :
            if sno=='0':
                title = request.form.get('title')
                subtitle = request.form.get('subtitle')
                content = request.form.get('content')
                author = request.form.get('author')
                img_url = request.form.get('img_url')
                date_today = str(date.today()).split('-')
                date_today.reverse()
                date_today = "-".join(date_today)
                slug = '-'.join((title+' by '+author).split(' '))
                new_post = Posts(title=title,subtitle=subtitle,content=content,slug=slug,author=author,date=date_today,img_url=img_url)
                db.session.add(new_post)
                db.session.commit()

            else:
                req_post = Posts.query.filter_by(sno=sno).first()
                req_post.title = request.form.get('title')
                req_post.subtitle = request.form.get('subtitle')
                req_post.content = request.form.get('content')
                req_post.slug = request.form.get('slug')
                req_post.author = request.form.get('author')
                req_post.date = datetime.now()
                req_post.img_url = request.form.get('img_url')
                db.session.commit()

            return redirect('/login')

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno,isLoggedIn = (True if 'user' in session else False))
    redirect('/login')

@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user']==params['admin_username']:
        Posts.query.filter_by(sno=sno).delete()
        db.session.commit()
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

app.run(debug=True)
