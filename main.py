from flask import Blueprint, render_template, request, redirect, flash
from flask.helpers import url_for
from .models import User, Product
from . import db
from flask_login import login_required, current_user

#! debug
import traceback
import logging

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, role=current_user.role)


@main.route('/warehouse')
@login_required
def warehouse():
    products = Product.query.all()
    return render_template('warehouse.html', products=products, role=current_user.role, name=current_user.name)


@main.route('/warehouse', methods=['POST'])
@login_required
def warehouse_post():
    name = request.form.get("name")
    description = request.form.get("description")
    price = int(request.form.get("price"))
    presence = int(request.form.get("presence"))
    type_name = request.form.get("type")

    try:
        new_product = Product(name=name, description=description, price=price, presence=presence, type_name=type_name)
        db.session.add(new_product)
        db.session.commit()
        flash('Product registered successfully.')
        return redirect(url_for('main.warehouse'))
    except Exception as e:
        db.session.rollback()
        flash('DB commit fail. Check logs!')
        return redirect(url_for('main.warehouse'))


@main.route('/admin')
@login_required
def admin():
    users = User.query.all()
    return render_template('admin.html', name=current_user.name, role=current_user.role, users=users)


@main.route('/admin/<int:id>', methods=["POST", "GET"])
def update(id):
    user = User.query.get(id)
    if request.method == 'POST':
        user.role = request.form.get("role")
        try:
            db.session.commit()
            return redirect(url_for('main.admin'))
        except:
            return "<h1>DB COMMIT FAIL.</h1>"
    else:
        return render_template("user_edit.html", user=user, role=current_user.role)
