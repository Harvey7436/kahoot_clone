from itertools import count
from re import S
import socket
from urllib.parse import urlparse
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app,db
from app.forms import LoginForm, SignupForm, QuizForm
from app.models import User, Quiz, Question, Answer, StudentHistory
from datetime import datetime
import random
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms

socketio = SocketIO(app, cors_allowed_origins='*')

def isCorrect(index, correctIndex):
    if index == correctIndex:
        return True
    else:
        return False


@app.route('/')
@app.route('/index')
@login_required
def index():
    if current_user.is_teacher:
        return redirect(url_for('teacher_home'))
    else:
        return redirect(url_for('student_home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        print(f'{form.username.data}')
        print(request.form['isTeacher'])
        user.set_password(form.password.data)
        user.check_teacher(request.form['isTeacher'])
        db.session.add(user)
        db.session.commit()
        flash('Login requested for user {}, tos={}'.format(
            form.username.data, form.tos.data))
        return redirect(url_for('index'))
    return render_template('sign_up.html', title='Sign Up', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('signin'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('sign_in.html', title='Sign In', form=form)


QUESTIONS = Question.query.all()
SCORE = 0
COUNT = 0

@app.route('/student/<quiz>', methods=['GET', 'POST'])
@login_required
def student(quiz):
    global SCORE, QUESTIONS, COUNT
    q = Quiz.query.get(quiz)
    QUESTIONS = q.questions
    question = QUESTIONS[COUNT]
    answer = Answer.query.filter(Answer.question_id==question.id).all()
    if request.method == 'GET':
        return render_template("student.html", title='Student', question=question, answer=answer, score=SCORE)
    else:
        print('POST')
        # Check if chosen answer is correct
        if request.form.get('button')=="True":
            print("Correct")
            SCORE +=1
        COUNT+=1
        
        # Check if there is another question afterwards
        if COUNT+1<=len(QUESTIONS):
            next_page = url_for('student', quiz=quiz, question=question, answer=answer, score=SCORE)
            return redirect(next_page)
        else:
            flash(f"Score= {SCORE}")
            dt = datetime.now()
            date = dt.strftime("%d-%b-%Y")
            time = dt.strftime("%H:%M:%S")
            stuhist = StudentHistory(date=date, time=time, score=SCORE, user=current_user, quiz=q, count=COUNT)
            db.session.add(stuhist)
            db.session.commit()
            SCORE=0
            COUNT = 0
            QUESTIONS = Question.query.all()
            next_page = url_for('index')
            return redirect(next_page)


@app.route('/teacher/<quiz>', methods=['GET', 'POST'])
@login_required
def teacher(quiz):
    form = QuizForm()
    if form.validate_on_submit():
        if int(quiz)>len(Quiz.query.all()):
            qu = Quiz(desc=f"Quiz {quiz}")
        else:
            qu = Quiz.query.get(quiz)
        question = Question(desc=form.question.data, quiz=qu)
        correctAnswer = request.form['answers']
        answerA = Answer(desc=form.answerA.data, isCorrect=isCorrect("0",correctAnswer), answer=question)
        answerB = Answer(desc=form.answerB.data, isCorrect=isCorrect("1",correctAnswer), answer=question)
        answerC = Answer(desc=form.answerC.data, isCorrect=isCorrect("2",correctAnswer), answer=question)
        answerD = Answer(desc=form.answerD.data, isCorrect=isCorrect("3",correctAnswer), answer=question)
        db.session.add(question)
        db.session.add(answerA)
        db.session.add(answerB)
        db.session.add(answerC)
        db.session.add(answerD)
        db.session.commit()
        print(qu)
        print(correctAnswer.isdigit())
        next_page= url_for('teacher', quiz=quiz,title='Teacher', form=form, user=current_user)
        return redirect(next_page)

    return render_template('teacher.html', title='Teacher', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/stu', methods=['GET', 'POST'])
@login_required
def studentsign():
    return render_template('student-access.html', title='Student')   

@app.route('/avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    return render_template('avatar.html', title='Avatar')   

@app.route('/stuhome', methods=['GET', 'POST'])
@login_required
def student_home():
    quiz=Quiz.query.all()
    if request.method == 'POST':
        print(request.form.get('pin'))
        q=request.form.get('pin')[0]
        pin=request.form.get('pin')[1:]
        next_page = url_for('pin_waiting', pin=pin, quiz=q)
        return redirect(next_page)
    else:
        return render_template('student_home.html', title='student_home', quiz=quiz) 


@app.route('/stuhist', methods=['GET', 'POST'])
@login_required
def student_history():
    if request.method == 'POST':
        if request.form.get('delete'):
            print(request.form.get('delete'))
            StudentHistory.query.filter_by(id=request.form.get('delete')).delete()
            db.session.commit()
            stuhist = StudentHistory.query.filter(StudentHistory.student_id==current_user.id).all()
            return render_template('student_history.html', title='student_history', student_history=stuhist)
        else:
            print(request.form.get('pin'))
            quiz=request.form.get('pin')[0]
            pin=request.form.get('pin')[1:]
            next_page = url_for('pin_waiting', pin=pin, quiz=quiz)
        return redirect(next_page)
    else:
        stuhist = StudentHistory.query.filter(StudentHistory.student_id==current_user.id).all()
        return render_template('student_history.html', title='student_history', student_history=stuhist)

@app.route('/teacherhome', methods=['GET', 'POST'])
@login_required
def teacher_home():
    quiz=Quiz.query.all()
    return render_template('teacher_home.html', title='teacher_home', quiz=quiz, new=len(quiz)+1) 


@app.route('/teacherhist', methods=['GET', 'POST'])
@login_required
def teacher_history():
    return render_template('teacher_history.html', title='teacher_history')          
 

@app.route('/waiting/<quiz>', methods=['GET', 'POST'])
@login_required
def waiting(quiz):
    next_page= url_for('pin_waiting', pin=random.randint(99999, 999999), quiz=quiz)
    return redirect(next_page)

@app.route('/waiting/<quiz>-<pin>', methods=['GET', 'POST'])
@login_required
def pin_waiting(pin, quiz):
    print(request.base_url)
    print(request.url)
    if request.method == 'GET':
        if current_user.is_teacher:
            return render_template('teacher_waiting.html',pin=pin, title='Teacher Wait', quiz=quiz)
        else:
            return render_template('stu_waiting.html',pin=pin, title='Student Wait', quiz=quiz)
    else:
        pass

@app.route('/waiting/<quiz>-<pin>/student', methods=['GET', 'POST'])
@login_required
def studentgame(quiz, pin):
    global SCORE, QUESTIONS, COUNT
    q = Quiz.query.get(quiz)
    QUESTIONS = q.questions
    question = QUESTIONS[COUNT]
    answer = Answer.query.filter(Answer.question_id==question.id).all()
    if request.method == 'GET':
        return render_template('student.html', quiz=quiz, question=question, answer=answer, score=SCORE, title='Student')
    else:
        print('POST')
        # Check if chosen answer is correct
        if request.form.get('button')=="True":
            print("Correct")
            SCORE +=1
        COUNT+=1
        
        # Check if there is another question afterwards
        if COUNT+1<=len(QUESTIONS):
            next_page = url_for('studentgame', quiz=quiz, question=question, answer=answer, score=SCORE, pin=pin)
            return redirect(next_page)
        else:
            flash(f"Score= {SCORE}")
            dt = datetime.now()
            date = dt.strftime("%d-%b-%Y")
            time = dt.strftime("%H:%M:%S")
            stuhist = StudentHistory(date=date, time=time, score=SCORE, user=current_user, quiz=q, count=COUNT)
            db.session.add(stuhist)
            db.session.commit()
            QUESTIONS = Question.query.all()
            next_page = url_for('waiting',pin=pin, title='Student Wait', quiz=quiz)
            SCORE=0
            COUNT = 0
            return redirect(next_page)

clients=[]

@socketio.on('my event')
def test_message(data):
    print(data)

@socketio.on('my broadcast event')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'}, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handleMessage(msg):
    print(f'Message {msg}')
    send(msg, broadcast=True)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('redirect')
def on_redirect(data):
    next_page = url_for('studentgame', quiz=data['quiz'], pin=data['room'])
    emit('redirect', {'url': next_page}, room=data['room'], include_self=False)

if __name__ == '__main__':
    socketio.run(app)


