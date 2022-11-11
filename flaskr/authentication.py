from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.db import get_db
from flaskr.forms import RegistrationForm, LoginForm

at_bp = Blueprint('authentication', __name__)

isLoggedIn = False

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
        tmp = False
        db = get_db()
        cr = db.cursor()
        cr.execute("SELECT LOGIN, PASSWORD FROM USERS")
        x = cr.fetchall()
        for user in x:
            if user[0] == form.login.data and user[1] == form.password.data:
                tmp = True
                break

        if not tmp:
            flash('Invalid Credentials, Please try again')
            return redirect(url_for('authentication.do_login_user'))
        if tmp:
            # TODO
            isLoggedIn = True
            print(isLoggedIn)
            return redirect(url_for('flights.airports'))

    return render_template('login.page.html', form=form)

