from flask import Blueprint, render_template, redirect, url_for, request

from flaskr import oracle_db

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
    return redirect(url_for('tickets.classes'))


@tickets_bp.route('/classes/update/<int:class_id>', methods=['GET', 'POST'])
def update_class(class_id: int):
    return redirect(url_for('tickets.classes'))


@tickets_bp.route('/classes/delete', methods=['POST'])
def delete_class():
    return redirect(url_for('tickets.classes'))
