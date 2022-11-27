from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError, InputRequired
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email', validators= [DataRequired()])
    isTeacher= SelectField('Status',choices=[(False,'Student'), (True,'Teacher')] ,validators=[DataRequired()])
    tos=BooleanField("Agree")
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different name')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class QuizForm(FlaskForm):
    question = StringField('Question', validators=[InputRequired()])
    answerA = StringField('A: ', validators=[InputRequired()])
    answerB = StringField('B: ', validators=[InputRequired()])
    answerC = StringField('C: ', validators=[InputRequired()])
    answerD = StringField('D: ', validators=[InputRequired()])
    submit = SubmitField('Create')