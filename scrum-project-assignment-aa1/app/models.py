from app import db, login
from datetime import date, datetime
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_teacher=db.Column(db.Boolean)
    student_history = db.relationship('StudentHistory', backref="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def check_teacher(self, bool):
        if bool == 'True':
            self.is_teacher = True
        else:
            self.is_teacher = False

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Quiz(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(120), index=True)
    questions = db.relationship('Question', backref='quiz')
    student_history = db.relationship('StudentHistory', backref="quiz")

    def __repr__(self):
        return '<Quiz {}>'.format(self.desc)

class Question(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    desc = db.Column(db.String(120), index=True)
    answers = db.relationship('Answer', backref='answer')

    def __repr__(self):
        return '<Question {}>'.format(self.desc)

class Answer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    desc = db.Column(db.String(120), index=True)
    isCorrect = db.Column(db.Boolean)

    def __repr__(self):
        return self.desc

class StudentHistory(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(120), index=True)
    time = db.Column(db.String(120), index=True)
    score = db.Column(db.Integer)
    count = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<StudentHistory Date: {self.date}, Quiz: {self.quiz_id}, Score: {self.score}, Student: {self.student_id}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))