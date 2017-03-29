# coding: utf-8
import re
import requests
from bs4 import BeautifulSoup
from . import app, db
from werkzeug import security
from functools import wraps
from app.models import User, Feed, Article, Comment
from app.forms import RegisterForm, LoginForm, SearchForm, FeedForm, SettingForm, CommentForm
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib2 import urlopen
from flask_paginate import Pagination
import json
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

'''
电影评论系统视图层
url                     功能
/;/home;/Home           主页，随机展示
/Login                  登录界面
/Logout                 登出用户
/Regist                 注册界面
/Search                 搜索
/AddFeed                新增RSS源
/PersonalSetting        用户个人信息
'''
#404页面处理，返回主页
@app.errorhandler(404)
def page_not_found(error):
    flash('该页面不存在')
    return redirect(url_for('Home'))

# 对所有访客可见,管理员与用户都用此界面登录
@app.route('/Login',methods=['POST','GET'])
def Login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('Login.html', form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.password_verification(form.password.data):
                login_user(user)
                if current_user.id == 1:
                    flash('管理员登录成功！')
                else:
                    flash('登录成功！')
                return redirect(url_for('Home'))
            flash('用户名或密码错误！')
            return render_template('Login.html',form=form)
        else:
            flash('请检查是否输入用户名与密码')
            return render_template('Login.html',form=form)

# 对登录用户可见,重定向到登录界面
@app.route('/Logout', methods=['POST','GET'])
@login_required
def Logout():
    logout_user()
    flash('您已经成功登出！')
    return redirect(url_for('Home'))

# 对所有访客可见，如果没有订阅，随机显示数据库中的Article
@app.route("/", methods=['POST', 'GET'])
@app.route('/Home', methods=['POST','GET'])
def Home(page = 1):
    article_list = Article.query.order_by('id').paginate(page, 4, False)
    return render_template('ArticleList.html', article_list = article_list)

# 对所有访客可见,用户注册，成功会跳转至主页面，否则回到本页面
@app.route('/Regist',methods=['POST','GET'])
def Regist():
    form = RegisterForm()
    if request.method == "GET":
        return render_template("Regist.html", form=form)

    if request.method == "POST":
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash('此用户名已被占用,请更换用户名注册')
                return redirect(url_for('Regist'))
            else:
                user = User(username=form.username.data, password=form.comfirm.data,
                            email=form.email.data)
                db.session.add(user)
                db.session.commit()
                flash('注册成功,跳转至主页')
                login_user(user)
                return redirect(url_for('Home'))
        else:
            flash("请检查是否输入全部内容、邮箱格式以及两个密码是否一致")
        return render_template('Regist.html',form=form)

@app.route('/MyComment/<int:page>', methods=["POST", "GET"])
@login_required
def MyComment(page = 1):
    comment = Comment.query.filter_by(user_id=current_user.id).paginate(page, 5, False)
    return render_template('MyComment.html', comment_list=comment)

@app.route('/ModifyComment/<comment_id>', methods=["POST", "GET"])
@login_required
def ModifyComment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    form = ChangeCommentForm()
    if request.method == "POST":

        if form.validate_on_submit():
            comment.title = form.title.data
            comment.content = form.content.data
            comment.rating = form.rating.data
            db.session.commit()
            flash("保存成功")
            return redirect(url_for("MyComment", page=1))
        else:
            flash("请输入评论内容")
            return redirect(url_for("ModifyComment", comment_id=comment_id))
    if request.method == "GET":
        return render_template('ModifyComment.html', form=form, comment=comment)

@app.route('/PersonalSetting', methods=["POST", "GET"])
@login_required
def PersonalSetting():
    form = SettingForm()
    if request.method=="POST":
        if form:
            #修改密码
            if form.old_password.data and form.password1.data and form.password2.data:
                if current_user.password_verification(form.old_password.data) and form.password2.data:
                    current_user.password_hash = generate_password_hash(form.password2.data)
                    db.session.commit()
                    flash('修改密码成功')
                else :
                    flash('与原密码不匹配，无法修改')
                    return redirect(url_for("PersonalSetting"))
            #修改邮箱地址
            if form.email.data:
                current_user.email = form.email.data
                db.session.commit()
                flash('修改邮箱成功')
            #修改电话号码
            if form.phone.data:
                current_user.phone = form.phone.data
                db.session.commit()
                flash('修改电话号码成功')
        return redirect(url_for("Home"))
    else:
        return render_template('PersonalSetting.html', form=form)


#对所有访客可见
@app.route('/Information/<name>', methods=["POST", "GET"])
def Information(name):
    movie = Movie.query.filter_by(name=name).first()
    if request.method == 'GET':
        comment_list = Comment.query.filter_by(movie_id=movie.id).all()
        form = CommentForm()
        return render_template('MovieInfo.html', form=form, movie=movie, comment_list=comment_list)

    if request.method == "POST":
    #发表评论
        if current_user.is_authenticated:
            form = CommentForm()
            if form.validate_on_submit():
                comment = Comment(date=datetime.date.today(), title=form.title.data, content=form.content.data,
                                  rating=form.rating.data, user_id=current_user.id, movie_id=movie.id)
                db.session.add(comment)
                db.session.commit()
                flash("评论发表成功")
                print "success"
            comment_list = Comment.query.filter_by(movie_id=movie.id).all()
            #if comment_list and flag:
            render_template('MovieInfo.html', form=form, movie=movie, comment_list=comment_list)
            return redirect(url_for('Information', name=movie.name))
        else:
            flash("请登录后发表评论")
            return redirect(url_for('Information', name=movie.name))
