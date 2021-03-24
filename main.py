from flask import Blueprint, render_template, request, redirect
from flask.helpers import url_for
from .models import User
from . import db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, role=current_user.role)


@main.route('/warehouse')
def warehouse():
    return render_template('warehouse.html')


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
