from flask import Blueprint, render_template, request
from flaskr.db import get_db
from flaskr.forms import RegistrationForm

at_bp = Blueprint('authentication', __name__)


@at_bp.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if request.method == 'POST':
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

    return render_template('registration.page.html', form=form)
