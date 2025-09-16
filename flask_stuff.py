from flask import Flask, session, redirect, url_for, request, render_template
from datetime import timedelta
from functools import wraps
from exceptions import PermissionDenied
from forum import Forum
from thread import Thread, ThreadPostLink
from post import Post, PostUpvotes
from user import User
from forum import Forum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base

engine = create_engine("sqlite:///forum.db")
Session = sessionmaker(bind=engine)
sql_session = Session()
Base.metadata.create_all(engine)
forum = Forum()
caesar = User('caesar@rome.com', 'venividivici7', 'Julius', 'Caesar', 1, 7, 12) #technically born 100 BC but that doesn't work
cleopatra = User('cleopatra@pharaoh.com', 'nile379%', 'Cleopatra', 'Philopator', 32, 1, 1) #added 101 to age to keep relative ages
brutus = User('brutus@rome.com', 'etmoibrute11', 'Marcus', 'Brutus', 16, 1, 1) #added 101 to age to keep relative ages
sql_session.add_all([caesar, cleopatra, brutus])
sql_session.add(forum)
sql_session.commit()
app = Flask(__name__, static_folder='static', template_folder='static/templates') 
app.secret_key = 'secret key' 
app.permanent_session_lifetime = timedelta(minutes=60)  # Set session timeout 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") == None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST']) 
@login_required
def index(): 
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower()
        pwd = request.form['password']
        fname = request.form['firstname']
        lname = request.form['lastname']
        year, month, day = request.form['birthday'].split('-')
        year = int(year)
        month = int(month)
        day = int(day)
        new_user = User(email, pwd, fname, lname, year, month, day)
        sql_session.add(new_user)
        sql_session.commit()
        session['user'] = sql_session.query(User).filter_by(fname=fname, lname=lname).first().get_id() #can only save user id, not full object
        return redirect('/')
    return render_template('register.html')

@app.route('/forum/<id>', methods=['GET', 'POST'])
@login_required
def forum(id):
    forum_object = sql_session.query(Forum).filter_by(id=id).first()
    title = forum_object.get_title()
    threads = forum_object.get_threads(sql_session)
    return render_template('forum.html', id=id, title=title, threads=threads)

@app.route('/thread/<id>', methods=['GET', 'POST'])
@login_required
def thread(id):
    return render_template('thread.html', id, title, posts)

if __name__ == '__main__': 
    app.run(debug=True) 