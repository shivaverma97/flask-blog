from datetime import datetime
from flask_blog import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable= False)
    password = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(120), nullable=False , default = 'default.jpg')
    posts = db.relationship('Post', backref = 'author', lazy = True)


    def get_reset_token(self, expire_sec = 360):
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'user({self.username},{self.email},{self.profile_pic})'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    photo =db.Column(db.String(240))
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    def __repr__(self):
        return f'post({self.title},{self.date_posted})'
