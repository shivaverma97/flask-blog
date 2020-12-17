from flask import render_template, url_for, flash, redirect, request, abort
import secrets
import os
from flask_blog import app, db, bcrypt, mail
from flask_blog.forms import RegistrationForm, LoginForm, UpdationForm, PostForm, ResetPasswordForm, RequestResetForm, Email_verify, validate_otp
from flask_blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from flask_mail import Message
import random
import string

otp = random.randint(000000,999999) 

@app.route("/home")
@login_required
def home():
    page = request.args.get('page',1, type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page= page, per_page = 5)
    # return ("<h1>welcome to my website, shiva here!!</h1>")
    return render_template('home.html', posts = posts , title = 'home page')

@app.route("/about")
def about():
    # return ("I am an engineer")
    return render_template('about.html', title = 'about page')

@app.route("/verify_email", methods = ['GET','POST'])
def verify_email():
    form = Email_verify()
    if form.validate_on_submit():
        email = form.email.data
        msg = Message('OTP',sender = 'username@gmail.com', recipients = [email])  
        msg.body = f'''Hello,
To continue creating your new account, please verify your email address by using the OTP given below.        
OTP : {str(otp)}
New account requires a verified email address so you can take full advantage of our Website.
*If you didn't recently attempt to create a new account with this email address, you can safely disregard this email. No new account will be made for {email}.'''  
        mail.send(msg)  
        flash(f'An OTP has been sent to {email}.','info')
        return redirect(url_for('confirm_otp'))
    return render_template('email_verify.html', title='verify email', form = form )

@app.route("/confirm_otp", methods = ['GET','POST'])
def confirm_otp():
    form = validate_otp()
    if form.validate_on_submit():
        user_otp =  form.otp.data 
        if otp == int(user_otp):  
            flash('Email has been verified','success')
            return redirect(url_for('register')) 
        else:     
            flash('OTP is incorrect','warning')
    return render_template('validate_otp.html',title='confirm OTP', form = form)    

@app.route("/register", methods=['GET','POST'])  # method is used to get and post the request from the server
def register():
    form = RegistrationForm()
    if current_user.is_authenticated :
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data , password = hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You can Login now.','success')
        return redirect(url_for("login"))
    return render_template('register.html', title='registration form', form = form)


@app.route("/", methods=['GET','POST'])
@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated :
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(username= form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page :                                # for user trying to access the account page without login
                flash(f'Logged in successfully as {user.username}','success')
                return redirect(next_page) 
            else:
                flash(f'Logged in successfully as {user.username}','success')        # for direct login
                return redirect(url_for('home'))
        else:
            flash('Entered wrong username or password, Try again','danger')
    return render_template('login.html', title= 'login form', form = form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))



def save_picture(form_displayPic):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_displayPic.filename)
    displayPicFn = random_hex + f_ext
    displayPicPath = os.path.join(app.root_path ,'static/profile_pics' , displayPicFn)
    
    output_size = (150,150)
    i = Image.open(form_displayPic)
    i.thumbnail(output_size)
    i.save(displayPicPath)

    return displayPicFn

def save_post_picture(form_uploadedPic):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_uploadedPic.filename)
    uploadedPicFn = random_hex + f_ext
    uploadedPicPath = os.path.join(app.root_path ,'static/uploaded_pics' , uploadedPicFn)
    form_uploadedPic.save(uploadedPicPath)
    # i = Image.open(form_uploadedPic)
    # i.save(uploadedPicPath)
    
    return uploadedPicFn

@app.route("/account", methods = ['GET','POST'])
@login_required                         # this is used to deny access of logged out users to access account info
def account():
    form = UpdationForm()
    image_file = url_for('static', filename='profile_pics/'+ current_user.profile_pic)
    if form.validate_on_submit():
        if form.display_pic.data:
            pic_file = save_picture(form.display_pic.data)
            current_user.profile_pic = pic_file
        current_user.username = form.username.data 
        current_user.email = form.email.data  
        db.session.commit()
        flash(f'Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='account info' , image_file = image_file, form = form)



@app.route("/post", methods = ['POST','GET'])
@login_required
def post():
    form = PostForm()
    post_user = Post(title = form.title.data , content = form.content.data , photo = form.photo_uploaded.data ,author = current_user)
    picture = url_for('static', filename = 'uploaded_pics/'f'{post_user.photo}')
    if form.validate_on_submit():
        if form.photo_uploaded.data:
            up_pic_file = save_post_picture(form.photo_uploaded.data)
            post_user.photo = up_pic_file
        db.session.add(post_user)
        db.session.commit()
        flash('Post has been created!','success')
        return redirect(url_for('home'))
    return render_template('post.html', title='post', form = form, legend = "What's on your mind?", picture = picture)


@app.route("/post/<int:post_id>")
@login_required
def postinfo(post_id):
    post_inf = Post.query.get_or_404(post_id)
    return render_template('postinfo.html',title='postInfo', post = post_inf)


@app.route("/post/<int:post_id>/update", methods = ['GET','POST'])
@login_required
def updatepost(post_id):
    post_inf = Post.query.get_or_404(post_id)
    if post_inf.author != current_user :
        abort(403)
    picture = url_for('static', filename = 'uploaded_pics/'f'{post_inf.photo}')    
    form = PostForm()
    if form.validate_on_submit():
        if form.photo_uploaded.data:
            pic_file = save_post_picture(form.photo_uploaded.data)
            post_inf.photo = pic_file
        post_inf.title = form.title.data
        post_inf.content = form.content.data
        db.session.commit()
        flash('Your post has been updated','success')
        return redirect(url_for('home'))
    elif request.method == 'GET' :
        form.title.data = post_inf.title
        form.content.data = post_inf.content
    return render_template('post.html', title='update post', form = form , legend ='Update post', picture = picture)


@app.route("/post/<int:post_id>/delete", methods = ['POST','GET'])
@login_required
def deletepost(post_id):
    post_inf = Post.query.get_or_404(post_id)
    if post_inf.author != current_user:
        abort(403)
    db.session.delete(post_inf)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('home'))



@app.route("/user_account/<string:username>" , methods=['GET'])
@login_required
def user_account(username):
    page = request.args.get('page', 1 , type = int)
    user = User.query.filter_by(username = username).first_or_404()
    image_file = url_for('static', filename='profile_pics/'+ user.profile_pic)
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page , per_page = 5)
    return render_template('user_account.html' , posts = posts , title = 'user account', user = user, image_file = image_file)


def send_verrification_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_pass' , token = token, _external = True)}

If you did not make that request then kindly ignore this email and no change will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods = ['GET', 'POST'])
def request_reset():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_verrification_email(user)
        flash(f'An Email has been sent to {user.email} with all the instructions.')
        return redirect(url_for('login'))
    return render_template('request_reset.html', title = 'request reset token', form = form)


@app.route("/reset_password/<token>", methods = ['GET','POST'])
def reset_pass(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash ('Token is either invalid or expired','warning')
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        flash('Your Password has been changed! You can Login now.','success')
        return redirect(url_for("login"))
    return render_template('reset_password.html', title='reset password', form = form)