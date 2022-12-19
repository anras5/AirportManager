from flask import Blueprint, render_template, redirect, url_for, request, flash

from flaskr.forms import RunwaysForm
from flaskr import oracle_db, constants as c

runways_bp = Blueprint('runways', __name__, url_prefix='/runways')


@runways_bp.route('/')
def main():
    return render_template('runways-index.page.html')


# -------------------------------------------------------------------------------------------------------------------- #
# RUNWAYS

@runways_bp.route('/runways')
def runways():
    headers, runways_list = oracle_db.select_runways()

    return render_template('runways-runways/runways-runways.page.html',
                           data=runways_list,
                           headers=headers)


@runways_bp.route('/runways/new', methods=['GET', 'POST'])
def new_runway():
    form = RunwaysForm()
    if form.validate_on_submit():
        # POST
        flash_message, flash_category, flash_type = oracle_db.insert_runway(form.nazwa.data,
                                                                            form.dlugosc.data,
                                                                            form.opis.data)

        flash(flash_message, flash_category)
        # TODO: catching unique keys exceptions
        if flash_category == c.ERROR:
            return redirect(url_for('runways.runways'))
        else:
            return redirect(url_for('runways.runways'))

    return render_template('runways-runways/runways-runways-new.page.html',
                           form=form)


@runways_bp.route('/runways/update/<int:runway_id>', methods=['GET', 'POST'])
def update_runway(runway_id: int):
    form = RunwaysForm()

    # get pas from db
    pas = oracle_db.select_runway(runway_id)

    if form.validate_on_submit():
        print("POST")
        # update runway
        flash_message, flash_category, flash_type = oracle_db.update_runway(runway_id,
                                                                            form.nazwa.data,
                                                                            form.dlugosc.data,
                                                                            form.opis.data)

        flash(flash_message, flash_category)
        # TODO: catching unique keys error
        if flash_category == c.ERROR:
            return render_template('runways-runways/runways-runways-update.page.html',
                                   form=form,
                                   pas=pas)
        else:
            return redirect(url_for('runways.runways'))

    print("GET")
    # set default values on the form
    form.nazwa.data = pas.nazwa
    form.dlugosc.data = pas.dlugosc
    form.opis.data = pas.opis

    return render_template('runways-runways/runways-runways-update.page.html',
                           form=form,
                           pas=pas)


@runways_bp.route('/runways/delete', methods=['POST'])
def delete_runway():
    print(request.form.get('runway_id'))
    return redirect(url_for('runways.main'))
