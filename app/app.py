from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db_manager import DBManager
from bson.objectid import ObjectId
import traceback
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'
db = DBManager()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

class User(UserMixin):
    def __init__(self, user_id, username, email, role):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role

def safe_iterable(value):
    """
    Check if value is iterable but NOT a string or a method/function.
    This prevents 'builtin_function_or_method object is not iterable' errors.
    """
    if isinstance(value, (str, bytes)):
        return False
    if callable(value):
        return False
    try:
        iter(value)
        return True
    except TypeError:
        return False

app.jinja_env.filters['safe_iterable'] = safe_iterable

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data['user_id'], user_data['username'], user_data['email'], user_data['role'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = db.authenticate_user(username, password)
        if user_data:
            user = User(user_data['user_id'], user_data['username'], user_data['email'], user_data['role'])
            login_user(user)
            flash(f'¡Bienvenido {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))
        
        try:
            user_id = db.create_user(username, email, password)
            flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    try:
        products = db.get_products()
        
        # Group products by category
        products_by_category = {}
        for product in products:
            category = product.get('category', 'Otros')
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product)
            
        return render_template('index.html', products_by_category=products_by_category)
    except TypeError as e:
        if "builtin_function_or_method" in str(e):
            app.logger.error(f"Iterable Error in Index: {e}")
            # Fallback to empty list or handle gracefully
            return render_template('index.html', products_by_category={})
        return f"Error de Tipo: {e}"
    except Exception as e:
        app.logger.error(f"General Error in Index: {e}")
        return f"Error conectando a BD: {e}"

@app.route('/orders')
@login_required
def orders():
    try:
        orders = db.get_user_orders(current_user.id)
        return render_template('orders.html', orders=orders)
    except Exception as e:
        return f"Error: {e}"

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    try:
        order = db.get_order_details(order_id)
        if not order:
            flash('Pedido no encontrado', 'danger')
            return redirect(url_for('orders'))
        
        if order['user_id'] != current_user.id and current_user.role != 'admin':
            flash('No tienes permiso para ver este pedido', 'danger')
            return redirect(url_for('orders'))
        
        return render_template('order_detail.html', order=order)
        return render_template('order_detail.html', order=order)
    except Exception as e:
        app.logger.error(f"Error in order_detail: {e}")
        app.logger.error(traceback.format_exc())
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('orders'))

@app.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
def pay_order(order_id):
    try:
        order = db.get_order_details(order_id)
        if not order:
            flash('Pedido no encontrado', 'danger')
            return redirect(url_for('orders'))
        
        if order['user_id'] != current_user.id:
            flash('No tienes permiso para pagar este pedido', 'danger')
            return redirect(url_for('orders'))
        
        if order['status'] != 'pending':
            flash('Este pedido no puede ser pagado', 'warning')
            return redirect(url_for('order_detail', order_id=order_id))
        
        payment_method = request.form.get('payment_method', 'credit_card')
        db.create_payment(order_id, order['total_amount'], payment_method)
        db.update_order_status(order_id, 'paid')
        
        flash('¡Pago procesado exitosamente!', 'success')
    except Exception as e:
        flash(f'Error al procesar pago: {str(e)}', 'danger')
    
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    try:
        order = db.get_order_details(order_id)
        if not order:
            flash('Pedido no encontrado', 'danger')
            return redirect(url_for('orders'))
        
        if order['user_id'] != current_user.id:
            flash('No tienes permiso para cancelar este pedido', 'danger')
            return redirect(url_for('orders'))
        
        if order['status'] not in ['pending', 'paid']:
            flash('Este pedido no puede ser cancelado', 'warning')
            return redirect(url_for('order_detail', order_id=order_id))
        
        db.cancel_order(order_id)
        flash('Pedido cancelado exitosamente', 'info')
    except Exception as e:
        flash(f'Error al cancelar pedido: {str(e)}', 'danger')
    
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/order/<int:order_id>/ship', methods=['POST'])
@login_required
def ship_order(order_id):
    try:
        if current_user.role != 'admin':
            flash('Solo los administradores pueden marcar pedidos como enviados', 'danger')
            return redirect(url_for('orders'))
        
        order = db.get_order_details(order_id)
        if not order:
            flash('Pedido no encontrado', 'danger')
            return redirect(url_for('orders'))
        
        if order['status'] != 'paid':
            flash('Solo se pueden enviar pedidos pagados', 'warning')
            return redirect(url_for('order_detail', order_id=order_id))
        
        db.update_order_status(order_id, 'shipped')
        flash('Pedido marcado como enviado', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/buy/<product_id>', methods=['POST'])
@login_required
def buy(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        price = float(request.form.get('price'))
        
        items = [{
            'product_id': ObjectId(product_id),
            'quantity': quantity,
            'price': price
        }]
        total_amount = price * quantity
        
        order_id = db.create_order(current_user.id, items, total_amount)
        flash(f'Pedido #{order_id} creado exitosamente!', 'success')
    except Exception as e:
        flash(f'Error al crear pedido: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
