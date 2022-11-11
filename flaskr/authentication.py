from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import UserMixin, login_user, logout_user
from flaskr.db import get_db
from flaskr.forms import RegistrationForm, LoginForm
from flaskr import login_manager
from . import db

at_bp = Blueprint('authentication', __name__)


class User(UserMixin):
    pass



@at_bp.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit(): # This also checks if the request method is POST
        login = form.login.data
        password = form.password.data

        db = get_db()
        cr = db.cursor()
        cr.execute("""INSERT INTO Users
                      VALUES
                      ((SELECT MAX(USER_ID) FROM Users)+1, :login, :password)
                    """, login=login, password=password)
        db.commit()
        cr.close()
        flash('Registration Succesful')
        return redirect(url_for('authentication.do_login_user'))
    return render_template('registration.page.html', form=form)

@at_bp.route('/login', methods=['GET', 'POST'])
def do_login_user():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(LOGIN=form.login.data).first()
        if not user:
            flash('Invalid Credentials, Please try again')
            return redirect(url_for('authentication.do_login_user'))
        login_user(user, form.stay_loggedin)
        return redirect(url_for('flights.airports'))
        # tmp = False
        # db = get_db()
        # cr = db.cursor()
        # cr.execute("SELECT LOGIN, PASSWORD FROM USERS")
        # x = cr.fetchall()
        # for user in x:
        #     if user[0] == form.login.data and user[1] == form.password.data:
        #         tmp = True
        #         break
        #
        # if not tmp:
        #     flash('Invalid Credentials, Please try again')
        #     return redirect(url_for('authentication.do_login_user'))
        # if tmp:
        #     login_user(form.login.data, form.stay_loggedin)
        #     return redirect(url_for('flights.airports'))

    return render_template('login.page.html', form=form)


@login_manager.user_loader
def load_user(login):
    db = get_db()
    cr = db.cursor()
    cr.execute("SELECT USER_ID FROM USERS WHERE Login = :login", [id])
    x = cr.fetchall()
    print(x[0])
    return int(x[0])
