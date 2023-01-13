from flask import Blueprint, render_template, redirect, url_for, request, flash

from flaskr import oracle_db
from flaskr.internal.helpers.forms import ClassForm
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
    return redirect(url_for('tickets.classes'))
