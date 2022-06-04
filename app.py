
from flask import Flask, render_template, request, flash, redirect,session,url_for
from sqlalchemy.engine import create_engine
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from database import User, Audio
from datetime import datetime
import os
from utils import *


app = Flask(__name__)
app.secret_key = 'youareunoworotohoy'
app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'wav','mp3'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),"static/uploads/")
app.config['SPECTROGRAM'] = os.path.join(os.getcwd(),"static/spectrograms/")
app.config['WAVELET'] = os.path.join(os.getcwd(),"static/wavelets/")

def opendb():
    engine = create_engine("sqlite:///dmb.sqlite")
    Session = sessionmaker(bind=engine)
    return Session()

def logged_in():
    if session.get('is_auth',False):
        return True
    return False

def login_user(user,remember=True):
    session['is_auth'] = True
    session['username'] = user.username
    session['email'] = user.email
    session['id'] = user.id
    if remember:
        session.permanent = True

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_audio_file(filename, upload_path):
    db = opendb()
    user = db.query(User).filter_by(id=session['id']).first()
    upload = Audio(
        name = filename,
        path=upload_path, 
        ftype = filename.rsplit('.', 1)[1].lower(),
        user = user.id,
        spath = session['spath'],
        wpath = session['wpath']
    )
    db.add(upload)
    db.commit()
    db.close()

def predict_genre(path):
    spath = spectrogram(path,app.config['SPECTROGRAM'])
    wpath = wavelet(path,app.config['WAVELET'])
    session['spath'] = spath
    session['wpath'] = wpath
    out = classify(spath,wpath,app.config['SPECTROGRAM'])
    pos = np.argmax(out)
    genre =labels[pos]
    print(genre)
    session['genre'] = genre


@app.route('/login', methods=['GET', 'POST'])
def login():
    if logged_in():
        return redirect('/logout')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            db = opendb()
            user = db.query(User).filter_by(username=username)
            if user.count() == 1:
                if user.first().password == password:
                    login_user(user.first(), remember=True)
                    flash('You are now logged in','success')
                    db.close()  
                    return redirect(url_for('index'))
            flash('Invalid username or password','danger')
        else:
            flash('Please enter a username and password','danger')
        db.close()  
        return redirect(url_for('login'))
    return render_template('login.html', title='Sign In')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        cpassword = request.form.get('cpassword')
        password = request.form.get('password')
        # print(cpassword, password, cpassword==password)
        if username and password and cpassword and email:
            if cpassword != password:
                flash('Password do not match','danger')
                return redirect('/register')
            else:
                db = opendb()
                if db.query(User).filter_by(email=email).first() is not None:
                    flash('Please use a different email address','danger')
                    return redirect('/register')
                elif db.query(User).filter_by(username=username).first() is not None:
                    flash('Please use a different username','danger')
                    return redirect('/register')
                else:
                    db = opendb()
                    user = User(username=username, email=email,password=password)
                    db.add(user)
                    db.commit()
                    db.close()
                    flash('Congratulations, you are now a registered user!','success')
                    return redirect(url_for('login'))
        else:
            flash('Fill all the fields','danger')
            return redirect('/register')

    return render_template('register.html', title='Sign Up page')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.pop('is_auth',None)
    return redirect('/login')

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():
    if not logged_in():
        return redirect('/login')
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            flash('No file uploaded','danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no file selected','danger')
            return redirect(request.url)
        if file and allowed_files(file.filename):
            print(file.filename)
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            session['uploaded_file'] = upload_path
            predict_genre(upload_path)
            save_audio_file(filename, upload_path)
            flash('file genre predicted','success')
            return redirect(url_for('index'))
        else:
            flash('wrong file selected, only WAV and MP3 files allowed','danger')
            return redirect(request.url)
   
    return render_template('index.html',title='Upload Audio files')


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)