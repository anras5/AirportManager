from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.db import get_db
from flaskr.forms import RegistrationForm

at_bp = Blueprint('authentication', __name__)


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
        return redirect(url_for('authentication.login_user'))
    return render_template('registration.page.html', form=form)

@at_bp.route('/login', methods=['GET', 'POST'])
def login_user():
    return render_template('login.page.html')
