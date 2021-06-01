from flask import Blueprint, render_template, request, redirect, flash, send_from_directory
from flask.helpers import url_for
from flask.templating import render_template_string
from .models import User, Product, User_roles, Product_types, Cart, Cart_product
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import settigns
import os

main = Blueprint('main', __name__)


def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'), 'favicon.ico')

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
    product_types = Product_types.query.all()
    return render_template('warehouse.html', products=products, role=current_user.role, name=current_user.name, ptypes = product_types)


@main.route('/warehouse', methods=['POST'])
@login_required
def warehouse_post():
    name = request.form.get("name")
    description = request.form.get("description")
    price = int(request.form.get("price"))
    presence = int(request.form.get("presence"))
    type_id = request.form.get("type")
    file = request.files['file']
    
    try:
        # photo upload
        if file and is_filename_allowed(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(settigns.RESOURCE_DIR, filename))

            # registering product
            new_product = Product(name=name, description=description, price=price, presence=presence, type_id=type_id, photo_url=filename)
            db.session.add(new_product)

            db.session.commit()
            flash('Product registered successfully.')
            return redirect(url_for('main.warehouse'))
        else:
            flash('Error while uploading photo.')
            return redirect(url_for('main.warehouse'))
    except Exception as e:
        db.session.rollback()
        flash('DB commit fail. Check logs!')
        return redirect(url_for('main.warehouse'))


@main.route('/warehouse/<int:id>', methods=["POST", "GET"])
@login_required
def update_product(id):
    product = Product.query.get(id)
    product_types = Product_types.query.all()
    if request.method == 'POST':
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = int(request.form.get("price"))
        product.presence = int(request.form.get("presence"))
        product.type_id = request.form.get("type")
        try:
            db.session.commit()
            return redirect(url_for('main.warehouse'))
        except:
            return "<h1>DB COMMIT FAIL.</h1>"
    else:
        return render_template("product_edit.html", product=product, role=current_user.role, ptypes=product_types)


@main.route('/warehouse/<int:id>/delete')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)

    try:
        db.session.delete(product)
        db.session.commit()
        flash("Продукт удален")
        return redirect(url_for("main.warehouse"))
    except:
        return "Произошла ошибка!"
    
    
def is_filename_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in settigns.ALLOWED_EXTENSIONS


@main.route('/admin')
@login_required
def admin():
    users = User.query.all()
    role = User_roles.query.get(current_user.role)
    return render_template('admin.html', name=current_user.name, role=role, users=users)


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


@main.route("/store")
@login_required
def store():
    max_steps = db.session.query(Product_types).order_by(Product_types.type_id.desc()).first().type_id
    step = current_user.step;
    if step <= max_steps:
        products = Product.query.filter_by(type_id=step)
        if products.count() != 0:
            step_name = Product_types.query.get(products[0].type_id).type_name
            return render_template('store.html', products=products, step_name=step_name, status="ok")
        else:
            return render_template('store.html', status="no products available")
    else:
        return redirect(url_for('main.cart'))


@main.route("/store/<int:id>", methods=["GET"])
@login_required
def add_to_cart(id):
    current_user.step = Product.query.get(id).type_id + 1;
    new_cart_product = Cart_product(cart_id=Cart.query.filter_by(user_id=current_user.id).first().id, product_id=id)
    db.session.add(new_cart_product)
    try:
        db.session.commit()
        return redirect(url_for("main.store"))
    except:
        return "<h1>DB COMMIT FAIL. Please report this bug!</h1>"


@main.route("/cart")
@login_required
def cart():
    step = current_user.step;
    max_steps = db.session.query(Product_types).order_by(Product_types.type_id.desc()).first().type_id
    if step >= max_steps:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        cart_products = Cart_product.query.filter_by(cart_id=cart.id)
        products = []
        presence = True
        price = 0
        for p in cart_products:
            product = Product.query.get(p.product_id)
            products.append(product)
            price += product.price
            if product.presence <= 0:
                presence = False
        return render_template("cart.html", products=products, progress=cart.progress, presence=presence, price=price, is_paid=cart.is_paid)
    else:
        return redirect(url_for('main.store'))


@main.route("/cart", methods=['POST'])
@login_required
def complete_order():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart_products = Cart_product.query.filter_by(cart_id=cart.id)
    for p in cart_products:
        product = Product.query.get(p.product_id)
        product.presence = product.presence - 1
    
    Cart_product.query.filter_by(cart_id=cart.id).delete()
    current_user.step = 1
    cart.progress = 10
    cart.is_paid = False
    db.session.commit()

    return redirect(url_for("main.end"))


@main.route("/cart/payment")
@login_required
def complete_payment():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart.is_paid = True
    db.session.commit()
    flash("Успешная оплата!")
    return redirect(url_for("main.cart"))

@main.route("/orders")
@login_required
def orders():
    max_steps = db.session.query(Product_types).order_by(Product_types.type_id.desc()).first().type_id
    users = User.query.filter_by(step=max_steps+1)
    data = []
    for user in users:
        cart = Cart.query.filter_by(user_id=user.id).first()
        cart_products = Cart_product.query.filter_by(cart_id=cart.id)
        info = [user, cart.progress]
        for p in cart_products:
            product = Product.query.get(p.product_id)
            info.append(product)
        data.append(info)
    return render_template("orders.html", role=current_user.role, data=data, max_steps=max_steps)


@main.route("/orders", methods=['POST'])
@login_required
def change_progress():
    user_id = request.form.get("id")
    progress = request.form.get("progress")
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    cart.progress = progress
    db.session.commit()
    return redirect(url_for("main.orders"))


@main.route("/end")
@login_required
def end():
    return render_template("end.html")