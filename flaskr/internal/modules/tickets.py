from flask import Blueprint, render_template, redirect, url_for, request, flash

from flaskr import oracle_db
from flaskr.internal.helpers.forms import ClassForm, PassengerForm
from flaskr.internal.helpers import constants as c

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


@tickets_bp.route('/')
def main():
    return render_template('tickets-index.page.html')


# -------------------------------------------------------------------------------------------------------------------- #
# CLASSES

@tickets_bp.route('/classes')
def classes():
    headers, classes_list = oracle_db.select_classes()

    return render_template('tickets-classes/tickets-classes.page.html',
                           data=classes_list,
                           headers=headers)


@tickets_bp.route('/classes/new', methods=['GET', 'POST'])
def new_class():
    form = ClassForm()
    if form.validate_on_submit():
        # POST

        flash_message, flash_category, flash_type = oracle_db.insert_class(form.nazwa.data,
                                                                           form.obsluga.data,
                                                                           form.komfort.data,
                                                                           form.cena.data)

        flash(flash_message, flash_category)
        if flash_type == c.KLASA_UN_NAZWA:
            form.nazwa.data = ""
            return render_template("tickets-classes/tickets-classes-new.page.html",
                                   form=form)
        else:
            return redirect(url_for("tickets.classes"))

    return render_template("tickets-classes/tickets-classes-new.page.html",
                           form=form)


@tickets_bp.route('/classes/update/<int:class_id>', methods=['GET', 'POST'])
def update_class(class_id: int):
    form = ClassForm()

    # get class from db
    class_ = oracle_db.select_class(class_id)

    if form.validate_on_submit():
        # update class
        flash_message, flash_category, flash_type = oracle_db.update_class(class_id,
                                                                           form.nazwa.data,
                                                                           form.obsluga.data,
                                                                           form.komfort.data,
                                                                           form.cena.data)

        flash(flash_message, flash_category)
        if flash_type == c.KLASA_UN_NAZWA:
            # duplicated nazwa in db
            form.nazwa.data = ""
            return render_template("tickets-classes/tickets-classes-update.page.html",
                                   form=form,
                                   klasa=class_)
        else:
            # success
            return redirect(url_for('tickets.classes'))

    # set default values on the form
    form.nazwa.data = class_.nazwa
    form.obsluga.data = class_.obsluga
    form.komfort.data = class_.komfort
    form.cena.data = class_.cena

    return render_template("tickets-classes/tickets-classes-update.page.html",
                           form=form,
                           klasa=class_)


@tickets_bp.route('/classes/delete', methods=['POST'])
def delete_class():
    # get class id from parameters
    parameters = request.form
    class_id = parameters.get('class_id', '')
    if not class_id:
        flash("Błąd - nie podano klasy do usunięcia", category=c.ERROR)
        return redirect(url_for('tickets.classes'))

    # delete model from database
    flash_messsage, flash_category = oracle_db.delete_class(class_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('tickets.classes'))


# -------------------------------------------------------------------------------------------------------------------- #
# PASSENGERS

@tickets_bp.route('/passengers')
def passengers():
    headers, passengers_list = oracle_db.select_passengers()

    return render_template('tickets-passengers/tickets-passengers.page.html',
                           data=passengers_list,
                           headers=headers)


@tickets_bp.route('/passengers/new', methods=['GET', 'POST'])
def new_passenger():
    form = PassengerForm()
    if form.validate_on_submit():
        # POST

        flash_message, flash_category, flash_type = oracle_db.insert_passenger(form.login.data,
                                                                               form.haslo.data,
                                                                               form.imie.data,
                                                                               form.nazwisko.data,
                                                                               form.pesel.data,
                                                                               form.data_urodzenia.data)

        flash(flash_message, flash_category)
        if flash_type == c.PASAZER_UN_LOGIN:
            form.login.data = ""
            return render_template("tickets-passengers/tickets-passengers-new.page.html",
                                   form=form)
        if flash_type == c.PASAZER_UN_PESEL:
            form.pesel.data = ""
            return render_template("tickets-passengers/tickets-passengers-new.page.html",
                                   form=form)
        else:
            return redirect(url_for("tickets.passengers"))

    return render_template("tickets-passengers/tickets-passengers-new.page.html",
                           form=form)


@tickets_bp.route('/passengers/update/<int:passenger_id>', methods=['GET', 'POST'])
def update_passenger(passenger_id: int):
    form = PassengerForm()

    # get passenger from db
    passenger = oracle_db.select_passenger(passenger_id)

    if form.validate_on_submit():
        # update class
        flash_message, flash_category, flash_type = oracle_db.update_passenger(passenger_id,
                                                                               form.login.data,
                                                                               form.haslo.data,
                                                                               form.imie.data,
                                                                               form.nazwisko.data,
                                                                               form.pesel.data,
                                                                               form.data_urodzenia.data)

        flash(flash_message, flash_category)
        if flash_type == c.PASAZER_UN_LOGIN:
            form.login.data = ""
            return render_template("tickets-passengers/tickets-passengers-update.page.html",
                                   form=form,
                                   pasazer=passenger)
        if flash_type == c.PASAZER_UN_PESEL:
            form.pesel.data = ""
            return render_template("tickets-passengers/tickets-passengers-update.page.html",
                                   form=form,
                                   pasazer=passenger)
        else:
            return redirect(url_for("tickets.passengers"))

    # set default values on the form
    form.login.data = passenger.login
    form.haslo.data = passenger.haslo
    form.imie.data = passenger.imie
    form.nazwisko.data = passenger.nazwisko
    form.pesel.data = passenger.pesel
    form.data_urodzenia.data = passenger.data_urodzenia

    return render_template("tickets-passengers/tickets-passengers-update.page.html",
                           form=form,
                           pasazer=passenger)


@tickets_bp.route('/passengers/delete', methods=['POST'])
def delete_passenger():
    # get passenger id from parameters
    parameters = request.form
    passenger_id = parameters.get('passenger_id', '')
    if not passenger_id:
        flash("Błąd - nie podano pasażera do usunięcia", category=c.ERROR)
        return redirect(url_for('tickets.passengers'))

    # delete model from database
    flash_messsage, flash_category = oracle_db.delete_passenger(passenger_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('tickets.passengers'))


@tickets_bp.route('/passengers/<int:passenger_id>/tickets')
def passenger_tickets(passenger_id: int):
    # get passenger's tickets
    headers, tickets_list = oracle_db.select_tickets_by_passenger(passenger_id)
    passenger = oracle_db.select_passenger(passenger_id)
    return render_template('tickets-passengers/tickets-passengers-tickets.page.html',
                           passenger=passenger,
                           headers=headers,
                           data=tickets_list)


@tickets_bp.route('/passengers/<int:passenger_id>/tickets/new', methods=['GET', 'POST'])
def passenger_new_ticket(passenger_id: int):
    headers, available_pools = oracle_db.select_pools_with_seats()
    passenger = oracle_db.select_passenger(passenger_id)

    if request.method == 'POST':
        pool_id = request.form.get('pool_id', '')
        if not pool_id:
            flash("Błąd - nie podano puli biletów dla nowego biletu", c.ERROR)
            return redirect(url_for('tickets.passenger_tickets', passenger_id=passenger_id))

        flash_message, flash_category = oracle_db.insert_ticket(passenger_id, pool_id)
        flash(flash_message, flash_category)
        return redirect(url_for('tickets.passenger_tickets', passenger_id=passenger_id))

    return render_template('tickets-passengers/tickets-passengers-tickets-new.page.html',
                           passenger=passenger,
                           headers=headers,
                           data=available_pools)


@tickets_bp.route('/passengers/tickets/delete')
def passenger_tickets_delete():
    return redirect(url_for('tickets.passenger_tickets'))


# -------------------------------------------------------------------------------------------------------------------- #
# POOLS

@tickets_bp.route('/pools')
def pools():
    headers, pools_list = oracle_db.select_pools()

    return render_template('tickets-pools/tickets-pools.page.html',
                           data=pools_list,
                           headers=headers)


# -------------------------------------------------------------------------------------------------------------------- #
# TICKETS

@tickets_bp.route('/tickets')
def tickets():
    headers, tickets_list = oracle_db.select_tickets()

    return render_template('tickets-tickets/tickets-tickets.page.html',
                           data=tickets_list,
                           headers=headers)
