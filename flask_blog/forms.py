from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from flask_login import current_user
from flask_blog.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField , TextAreaField, IntegerField 
from wtforms.validators import DataRequired, length, email, EqualTo , ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), length(min=2, max=20) ])
    email = StringField('Email ID', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username already exist! Please chose a different Username')
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Email already exist! Please chose a different Email')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    remember_me = BooleanField('Remember Me')

class UpdationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), length(min=2, max=20) ])
    email = StringField('Email ID', validators=[DataRequired(), email()])
    display_pic = FileField('Update Profile picture' , validators= [FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username :
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('Username already exist! Please chose a different Username')
    
    def validate_email(self, email):
        if email.data != current_user.email :
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('Email already exist! Please chose a different Email')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content' , validators= [DataRequired()])
    photo_uploaded = FileField('Post a Picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email ID', validators=[DataRequired(), email()])

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError("Email doesn't exist!! You need to register first.")
    
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset password')

class Email_verify(FlaskForm):
    email = StringField('Email ID', validators=[DataRequired(), email()])

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user :
            raise ValidationError("Email already exist!!")
    
    submit = SubmitField('Send OTP')

class validate_otp(FlaskForm):
    otp = IntegerField('OTP', validators=[DataRequired()])
    submit = SubmitField('Confirm OTP')