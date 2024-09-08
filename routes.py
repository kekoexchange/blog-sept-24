from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from . import app, db
from .models import User, Post, Comment
from .forms import LoginForm, RegistrationForm, EditPostForm, CommentForm

@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.all()
    return render_template('index.html', title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).all()
    return render_template('post.html', title=post.title, post=post, comments=comments)

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('You are not authorized to edit this post.')
        return redirect(url_for('index'))
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('Your post has been updated.')
        return redirect(url_for('post', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    return render_template('edit_post.html', title='Edit Post', form=form, post=post)

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', users=users)

