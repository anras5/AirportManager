from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flaskr.db import get_db
from flaskr.forms import RegistrationForm, LoginForm

at_bp = Blueprint('authentication', __name__)


@at_bp.route('/register', methods=['GET', 'POST'])
def register_user():
    if "user" in session:
        print("user in session")
    elif "admin" in session:
        print("admin in session")
    else:
        print('XD NIE')

    form = RegistrationForm()

    if form.validate_on_submit(): # This also checks if the request method is POST
        login = form.login.data
        password = form.password.data
        imie = form.imie.data
        nazwisko = form.nazwisko.data
        pesel = form.pesel.data
        dataurodzenia = form.dataurodzenia.data

        db = get_db()
        cr = db.cursor()
        cr.execute("""INSERT INTO Pasażer
                      VALUES
                      ((SELECT MAX(PASAŻER_ID) FROM Pasażer)+1, :login, :password, :imie, :nazwisko, :pesel, :dataurodzenia)
                    """, login=login, password=password, imie=imie, nazwisko=nazwisko, pesel=pesel, dataurodzenia=dataurodzenia)
        db.commit()
        cr.close()
        flash('Registration Succesful')
        return redirect(url_for('authentication.do_login_user'))
    return render_template('registration.page.html', form=form)


@at_bp.route('/login', methods=['GET', 'POST'])
def do_login_user():
    try:
        if session["user"] or session["admin"]:
            return redirect(url_for('flights.world_map'))
    except:
        pass

    form = LoginForm()

    if form.validate_on_submit():
        admin = False
        tmp = False
        db = get_db()
        cr = db.cursor()
        cr.execute("SELECT LOGIN, HASłO FROM Pasażer")
        x = cr.fetchall()
        for user in x:
            if user[0] == form.login.data and user[1] == form.password.data:
                tmp = True
                if user[0] == 'admin':
                    admin = True
                #if form.stay_loggedin.data:
                    #print("stay logged in")
                break

        if not tmp:
            flash('Invalid Credentials, Please try again')
            return redirect(url_for('authentication.do_login_user'))
        if tmp:
            if admin:
                session["admin"] = True
            session["user"] = True
            session["name"] = form.login.data
            return redirect(url_for('flights.world_map'))

    return render_template('login.page.html', form=form)

@at_bp.route('/logout')
def logout():
    print('in logout')

    session["user"] = False
    session["admin"] = False
    session["name"] = ""
    return redirect(url_for('authentication.do_login_user'))



