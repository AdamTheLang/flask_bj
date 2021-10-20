# auth.py

from flask import abort, Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from .models import Volunteers
from . import db, forms

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Volunteers.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect('/')


@auth.route('/add_user')
@login_required
def signup():
    return render_template('signup.html')


@auth.route('/add_user', methods=['POST'])
@login_required
def signup_post():

    if not current_user.admin:
        abort(401)

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = Volunteers.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = Volunteers(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect('/')


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_post():
    form = forms.ProfileForm(obj=current_user)

    if form.validate_on_submit():
        must_logout = False

        email = current_user.email
        user = Volunteers.query.filter_by(email=current_user.email).first()

        if not user: # if a user is found, we want to redirect back to signup page so user can try again
            flash("Oh dear. Something bad has happened, and I don't know what")
            abort(500)

        if form.new_password.data:
            must_logout = True
            user.password = generate_password_hash(form.new_password.data, method='sha256')
        if form.email.data and form.email.data != user.email:
            must_logout = True
            user.email = form.email.data

        user.name = form.name.data or user.name
        user.bj_nym = form.bj_nym.data or user.bj_nym
        user.states = form.states.data

        db.session.commit()
        if must_logout:
            logout_user()
        return redirect('/')

    return render_template('profile.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
