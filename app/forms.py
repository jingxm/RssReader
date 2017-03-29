# coding: utf-8

from flask_wtf import Form
from wtforms import IntegerField, StringField, SubmitField, PasswordField, BooleanField, DateField, FloatField
from wtforms.validators import Required, EqualTo, Email, DataRequired, Length

'''注册表单'''
class RegisterForm(Form):
    username = StringField('用户名', validators=[Length(min=4, max=25)])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('comfirm', message="密码必须匹配")])
    comfirm = PasswordField('确认密码')
    email = StringField('邮箱地址', validators=[Email()])
    submit = SubmitField('注册')

'''登录表单'''
class LoginForm(Form):
    email = StringField('邮件地址', validators=[Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住')
    submit = SubmitField('登录')

'''搜索表单'''
class SearchForm(Form):
    content = StringField('内容', validators=[DataRequired()])
    submit = SubmitField('搜索')

'''新增RSS源信息'''
class FeedForm(Form):
    rss_address = StringField('RSS订阅地址', validators=[DataRequired()])
    submit = SubmitField('新增')

'''管理个人信息'''
class SettingForm(Form):
    old_password = PasswordField('原密码', validators=[DataRequired()])
    password = PasswordField('密码', validators=[EqualTo('comfirm', message="密码必须匹配")])
    comfirm = PasswordField('确认密码')
    username = StringField('用户名', validators=[DataRequired()])
    submit = SubmitField('保存')

'''发表评论表单'''
class CommentForm(Form):
    content = StringField('评论', validators=[DataRequired()])
    submit = SubmitField('发表')
