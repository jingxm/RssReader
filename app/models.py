# coding:utf-8
from . import db, login_manager, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
from flask_table import Table, Col

'''
subscriptions = db.Table('Subscriptions',
    db.Column('feed_id', db.Integer, db.ForeignKey('feed.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
likes = db.Table('Likes', 
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), nullable=False, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
)
'''

#用户类，包括用户名、密码、邮箱、评论、收藏、订阅，其中每名用户会有若干评论、收藏、订阅。
class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    username = db.Column(db.String(64), nullable = False,  unique = True)
    password_hash = db.Column(db.String(200))

    comment = db.relationship('Comment', backref='users', lazy='dynamic')

    #, backref = db.backref('users', lazy = 'dynamic'), backref = db.backref('users', lazy = 'dynamic')
    subscriptions = db.relationship('Subscription', backref = 'users', lazy='dynamic')
    likes = db.relationship('Like', backref = 'users', lazy='dynamic')
    

    #注册callback，借此登录用户
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #简单的异常处理
    @property
    def password(self):
        raise AttributeError('读取密码发生错误！')

    #注册时将密码转为带盐哈希存储
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    #登录时验证密码
    def password_verification(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return 'This user is %r' % self.username

#订阅频道类，包括频道项目、订阅用户（与用户有多对多关系）。
class Feed(db.Model):
    __tablename__ = 'Feeds'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    link = db.Column(db.String(200))
    desc = db.Column(db.Text)
    rss_url = db.Column(db.String(200))
    img_url = db.Column(db.String(200))

    def __repr__(self):
        return 'This user is %r' % self.username

#频道文章类，包括对应频道（与评论一对多关系，与用户有多对多关系）。
class Article(db.Model):
    __tablename__ = 'Articles'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(200))
    content = db.Column(db.Text)
    title = db.Column(db.String(200))
    
    comment = db.relationship('Comment', backref="articles", lazy="dynamic")

    def __repr__(self):
        return 'This user is %r' % self.username

#评论类，包括内容、时间、对于用户和文章。
class Comment(db.Model):
    __tablename__ = 'Comments'
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    article_id = db.Column(db.Integer, db.ForeignKey(Article.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return 'This user is %r' % self.username



class Subscription(db.Model):
    __tablename__ = 'Subscriptions'
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key = True)
    feed_id = db.Column(db.Integer, db.ForeignKey(Feed.id), primary_key = True)

    user = db.relationship('User', backref = 'user_subscriptions', lazy = 'joined')
    feed = db.relationship('Feed', backref = 'feeds', lazy = 'joined')

    def __repr__(self):
        return 'This user is %r' % self.username

class Like(db.Model):
    __tablename__ = 'Likes'
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key = True)
    like_id = db.Column(db.Integer, db.ForeignKey(Article.id), primary_key = True)

    user = db.relationship('User', backref = 'user_likes', lazy = 'joined')
    like = db.relationship('Article', backref = 'articles', lazy = 'joined')

    def __repr__(self):
        return 'This user is %r' % self.username