from flask import render_template, request

from flaskr.auth.forms import RegistrationForm
from flaskr.auth import authentication as at
from flaskr.db import get_db


@at.route('/register', methods=['GET', 'POST'])
def register_user():
    login = None
    password = None
    form = RegistrationForm()

    if request.method == 'POST':
        login = form.login.data
        password = form.password.data

        db = get_db()
        cr = db.cursor()
        cr.execute(""" 
                    INSERT INTO Users
                    VALUES
                    ((SELECT MAX(USER_ID) FROM Users)+1, :login, :password)
                    """, [login, password])
        db.commit()

        cr.close()

    return render_template('registration.html', form=form)
