
from flask import Flask, flash, render_template, redirect, url_for, session, request, render_template_string
import flask_admin as admin
from flask_admin.menu import MenuLink
from flask_admin import expose, AdminIndexView
from flask_admin.contrib.pymongo import ModelView
from flask_pymongo import PyMongo
import bcrypt
import urllib

from datetime import datetime, timedelta

from forms import CustomerSignupForm, CustomerLoginForm, AddProductForm, AddProductFromAdminForm, ChangePasswordForm, OrderForm, UsersForm, ChangeAddress, ChangePersonalInfo


from flask_mongoengine import MongoEngine
from werkzeug.utils import secure_filename
import mongoengine as me
from bson.objectid import ObjectId
from flask_admin.menu import MenuLink
import gc


app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {"db": "myapp", }
db = MongoEngine(app)

app.config['MONGO_DBNAME'] = 'inventory_db'
app.config['MONGO_URI'] = "mongodb+srv://admin:" + urllib.parse.quote("Password@1") + \
                        "@cluster0.qyjhe.mongodb.net/inventory_db?retryWrites=true&w=majority"

mongo = PyMongo(app)


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        last_x_days_orders = revenue_last_x_days(3,0)
        past_x_days_orders = revenue_last_x_days(6,3)
        chart1_labels = []
        chart1_values = []
        chart2_labels = []
        chart2_values = []
        chart3_values = []
        chart4_values = []

        for order in last_x_days_orders:
            if "ordered_products" in order:
                for product in order["ordered_products"]:
                    if product["product_name"] in chart1_labels:
                        ind = chart1_labels.index(product["product_name"])
                        chart1_values[ind] = int(chart1_values[ind]) + int(product["quantity"])
                        chart3_values[ind] = float(chart3_values[ind]) + float(float(product["price"]) * int(product["quantity"]))
                    else:
                        chart1_labels.append(product["product_name"])
                        chart1_values.append(product["quantity"])
                        chart3_values.append(float(product["price"]) * int(product["quantity"]))

        for order in past_x_days_orders:
            if "ordered_products" in order:
                for product in order["ordered_products"]:
                    if product["product_name"] in chart2_labels:
                        ind = chart2_labels.index(product["product_name"])
                        chart2_values[ind] = int(chart2_values[ind]) + int(product["quantity"])
                        chart4_values[ind] = float(chart4_values[ind]) + float(float(product["price"]) * int(product["quantity"]))
                    else:
                        chart2_labels.append(product["product_name"])
                        chart2_values.append(product["quantity"])
                        chart4_values.append(float(product["price"]) * int(product["quantity"]))



        no_of_products = mongo.db.products.find({}).count()
        no_of_orders = mongo.db.orders.find({}).count()
        no_of_users = mongo.db.customers.find({}).count()
        current_revenue = sum(chart2_values)
        past_revenue = sum(chart4_values)
        sales_percentage = round(((current_revenue - past_revenue)/past_revenue),2)
        total_no_of_products_sold = sum(chart1_values)

        # highest_selling = mongo.db.orders.aggregate([
        #     { '$match': {}},
        #     { '$group': {'_id': "$ordered_products.product_name",
        #                    'totalSales': { '$sum' : "$ordered_products.quantity" } } },
        #     {'$unwind' : "$ordered_products.product_name"}
        # ])


        # for product in highest_selling:
        #     chart2_labels.append(product["_id"])
        #     chart2_values.append(product["totalSales"])
        all_labels = list(set(chart1_labels) | set(chart2_labels))
        for label in all_labels:
            if label not in chart1_labels:
                chart1_values.insert(all_labels.index(label),0)
                chart3_values.insert(all_labels.index(label), 0)
            if label not in chart2_labels:
                chart2_values.insert(all_labels.index(label),0)
                chart4_values.insert(all_labels.index(label), 0)
        return self.render('admin/index.html', chart1_labels=all_labels, chart1_values=chart1_values,
                           chart2_labels = all_labels, chart2_values = chart2_values,
                           chart3_labels = all_labels, chart3_values = chart3_values,
                           chart4_labels=all_labels, chart4_values=chart4_values,
                           no_of_products=no_of_products,no_of_orders=no_of_orders,
                           no_of_users=no_of_users, total_no_of_products_sold = total_no_of_products_sold,
                           sales_percentage = sales_percentage)


class ProductView(ModelView):
    column_list = ('product_name', 'category', 'description', 'size', 'barcode', 'brand', 'price', 'qty_in_stk', 'discount')
    form = AddProductFromAdminForm


class UserView(ModelView):
    column_list = ('username', 'email', 'first_name')
    #form_edit_rules = ('password')
    form = UsersForm

class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("products")



admin = admin.Admin(app, template_mode='bootstrap4',index_view=MyHomeView())
admin.add_link(MainIndexLink(name="Main Page"))
admin.add_view(ProductView(mongo.db.products))
admin.add_view(UserView(mongo.db.customers))
#admin.add_link(MenuLink(name='Back to Products', url=url_for('main.products')))


@app.context_processor
def utility_processor():

    def isAdmin():
        return True if 'isAdmin' in session and session["isAdmin"] == "1" else False
    return dict(isAdmin=isAdmin)






@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=e)


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html", error=e)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", error=e)

def revenue_last_x_days(start_days=7, end_days = 0):
    startDate = datetime.now() - timedelta(start_days)
    endDate = datetime.now() - timedelta(end_days)

    x = (
        mongo.db.orders.aggregate([
        {
            '$project': {
            'order_date': {
                '$dateFromString': {
                    'dateString': '$order_date'
                    }
                },
                'price':1,
                'quantity':1,
                'ordered_products':1
            }
        },
        {
            '$match': {
                'order_date': {'$gte': startDate, '$lte': endDate}
            }
        }
        ])
    )
    return x



def promo_price(price, discount):
    discounted_price = price - (price * (discount/100))
    new_price = price - discounted_price
    return new_price


@app.route('/')
def index():
    try:
        products_list = mongo.db.products
        all_products = products_list.find({"discount": {"$gt": 0}})

        return render_template('index.html', title='Home', products=all_products)
    except Exception as e:
        return str(e)


@app.route('/signup_customer/', methods=["GET", "POST"])
def signup_customer():
    try:
        form = CustomerSignupForm()
        if request.method == "POST":
            customers = mongo.db.customers
            email = form.email.data
            password = form.password.data
            confirm_password = form.confirm_password.data
            hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            existing_customer = customers.find_one({'email': email})

            if password == confirm_password:
                if existing_customer:
                    error = "That email is already registered. Sign in or choose another email."
                    flash(error)
                    return render_template("signup_customer.html", title='Customer Signup', form=form)
                else:
                    customers.insert_one({'email': email, 'password': hashed_password, 'username': email, 'active': 1,
                                          'create_date': formatted_date})
                    session['logged_in'] = True
                    session['isAdmin'] = True
                    session['email'] = email
                    flash("Welcome " + session['email'] + " Thanks for signing up!")
                    return redirect(url_for('index'))
            else:
                error = "Passwords must match."
                flash(error)
                return render_template("signup_customer.html", title='Customer Signup', form=form)

        return render_template('signup_customer.html', title='Customer Signup', form=form)

    except Exception as e:
        return str(e)


@app.route('/login_customer/', methods=["GET", "POST"])
def login_customer():
    try:
        form = CustomerLoginForm()
        if request.method == "POST":
            customers = mongo.db.customers
            email = form.email.data
            customer = customers.find_one({'email': email})
            if customer:
                if bcrypt.checkpw(form.password.data.encode('utf-8'), customer['password']):
                    if customer['active']:
                        session['logged_in'] = True
                        if 'isAdmin' in customer:
                            session['isAdmin'] = customer['isAdmin']
                        session['email'] = email
                        if 'first_name' in customer:
                            session['first_name'] = customer['first_name']
                        flash('Logged in successfully!')
                        return redirect(url_for('products'))
                    else:
                        flash("Account is not active")
                else:
                    flash("Invalid credentials. Try again")
            else:
                flash("Invalid credentials. Try again")
        return render_template('login_customer.html', title='Login Customer', form=form)
    except Exception as e:
        return str(e)


@app.route("/logout/")
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('index'))


@app.route('/products/')
def products():
    try:
        products_list = mongo.db.products
        all_products = products_list.find({})
        all_categories = products_list.distinct("category")
        return render_template('products.html', title='Products', products=all_products, categories=all_categories)
    except Exception as e:
        return str(e)


@app.route('/product_detail/', methods = ["POST"])
def product_detail():
    try:
        if request.method == "POST":
            id = request.data
            id = id.decode("utf-8")
            product = mongo.db.products.find_one({'_id': ObjectId(id)})
            #product = jsonify(product)
            #product = request.json['data']
        return  render_template('includes/product_modal.html', product = product)
    except Exception as e:
        return str(e)


@app.route('/product_page/<selected>', methods=['GET'])
def product_page(selected):
    product = mongo.db.products.find(
        {"barcode": selected}
    )
    return render_template('product_page.html', product=product)


@app.route('/personal_info/', methods= ["GET","POST"])
def personal_info():
    try:
        customer_list = mongo.db.customers
        all_customers=customer_list.find_one({'email': session['email']})
        all_orders = mongo.db.orders
        order = all_orders.find_one({'customer': session['email']})
        return render_template('personal_info.html', title='Personal Information', customers=all_customers,order=order)
    except Exception as e:
        return str(e)


    # if all_orders.findOne({'customer': session['email']}):
    #     order = all_orders.find({'customer': session['email']})




@app.route('/address_info/', methods= ["GET","POST"])
def address_info():
    form=ChangeAddress()
    all_orders = mongo.db.orders
    order = all_orders.find_one({'customer': session['email']})
    if request.method == "POST":
        if form.validate_on_submit():
            flash("Address information changed")
        #tpl1 = render_template_string("{% extends 'my_account.html' %}", content="name")
        return render_template('address_info_return.html', title='Address Information',order=order)
    return render_template('address_info.html', title='Address Information',order=order)




        #tpl1 = render_template_string("{% extends 'my_account.html' %}", content="name")







@app.route('/payment_info/')
def payment_info():
    return render_template('payment_info.html', title='Payment Information')


@app.route('/order_history/')
def order_history():
    try:
        all_orders = mongo.db.orders
        all_products = mongo.db.products
        order={}
        products={}
        item1=[]



        if all_orders.find({'customer':session['email']}):
            order = list(all_orders.find({'customer': session['email']}))
            #order_items=order.items()

            #for x in order:
                #if 'ordered_products' in x:
                    #for item in x['ordered_products']:
                        #item1.append(item)

        return render_template('includes/order_history.html', title='Order History', order=order, product=item1)







    except Exception as e:
        return str(e)



@app.route('/products_suggestions/', methods= ["GET","POST"])
def product_suggestion():
    return render_template('includes/products_suggestions.html', title='Product Suggestions')

@app.route('/change_password/', methods= ["GET","POST"])
def change_password():
    try:
        form = ChangePasswordForm()
        if request.method == "POST":
            if form.validate_on_submit():
                print("Form Valid")

            flash("Password Changed")

        return render_template('change_password.html', title='Change Password', form=form)
    except Exception as e:
        return str(e)





@app.route('/address_change/', methods= ["GET", "POST"])
def change_address():
    try:
        form = ChangeAddress()
        if request.method == "GET":
            return render_template('includes/address_change.html', title='Edit Address', form=form)
    except Exception as e:
        return str(e)



@app.route('/address_info_return/', methods=["GET"])
def address_info_return():
    return render_template('address_info_return.html', title='Address information')



@app.route('/personal_info_change/', methods= ["GET", "POST"])
def change_info():
    try:
        form = ChangePersonalInfo()
        all_orders = mongo.db.orders
        order = all_orders.find_one({'customer': session['email']})
        if request.method == "POST":
            orders= mongo.db.orders
            first_name=form.firstName.data
            middle_name=form.middleName.data
            last_name=form.lastName.data
            email_id=form.emailId.data
            phone_no=form.phoneNo.data
            return render_template('includes/personal_info_change.html', title='Edit Personal Info', form=form,order=order)
        return render_template('includes/personal_info_change.html', title='Edit Personal Info', form=form, order=order)
    except Exception as e:
        return str(e)





@app.route('/shipping_info/',methods=["GET"])
def shipping_info():
    all_orders = mongo.db.orders
    order = list(all_orders.find({'customer': session['email']}))

    return render_template('includes/shipping_info.html', title='Order History', order=order)






@app.route('/my_account/')
def my_account():
    pages = generate_page_list()
    return render_template('my_account.html', title='Account', pages=pages)


@app.route('/admin_panel/')
def admin_panel():
    pages = generate_admin_page_list()
    return render_template('admin_panel.html', title='Admin Panel', pages=pages)


def generate_page_list():
    pages = [
        {"name": "Personal Info", "url": url_for(
            "personal_info")
         },
        {"name": "Address Info", "url": url_for(
            "address_info")
         },
        {"name": "Payment Info", "url": url_for(
            "payment_info")
         },
        {"name": "Change Password", "url": url_for(
            "change_password")
         },
        {"name": "Order History", "url": url_for(
            "order_history")
         },
        # {"name": "Recommended For You", "url": url_for(
        #    "product_suggestion")
        #  },
        # {"name": "Ratings by you", "url": url_for(
        #     "payment_info")
         # },
    ]
    return pages


def generate_admin_page_list():
    pages = [
        {"name": "Manage users", "url": url_for(
            "personal_info")
         },
        {"name": "Manage Products", "url": url_for(
            "address_info")
         },

    ]
    return pages


@app.route('/product_list/')
def product_list():
    try:
        products_list = mongo.db.products
        all_products = products_list.find({})
        return render_template('admin/product_list.html', title='Product List', products=all_products)
    except Exception as e:
        return str(e)


@app.route('/add_product/', methods=["GET", "POST"])
def add_product():
    try:
        form = AddProductForm()

        #  if form.validate_on_submit(): check form if valid on submit before proceeding

        if request.method == "POST":
            products_list = mongo.db.products
            product_name = form.product_name.data
            product_desc = form.description.data
            barcode = form.barcode.data
            brand = form.brand.data
            price = form.price.data
            size = form.size.data
            description = form.description.data
            discount = form.discount.data
            # get file data
            file = form.image.data
            if file:
                filename = file.filename
                form.image.data.save('static/images/ProductImages/' + barcode + '.jpg')
                image = filename

            products_list.insert_one(
                {'product_name': product_name, 'barcode': barcode, 'brand': brand, 'price': price, 'size': size,
                 'description': description, 'discount': discount, 'image': image}
            )
            flash(product_name + " added!")
            return redirect(url_for('products'))

        return render_template('admin/add_product.html', title='Add Product', form=form)

    except Exception as e:
        return str(e)


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    try:
        products_list = mongo.db.products
        quantity = int(request.form['quantity'])
        barcode = request.form['barcode']

        # validate the received values
        if quantity and barcode and request.method == 'POST':
            row = products_list.find_one({'barcode': barcode})

            unit_price = float('{:,.2f}'.format(row['price'] - row['price'] * row['discount'] / 100))

            itemArray = {

                row['barcode']: {'product_name': row['product_name'], 'barcode': row['barcode'], 'quantity': quantity,
                                 'price': unit_price, 'image': row['image'], 'total_price': quantity * unit_price}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:

                if row['barcode'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['barcode'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * unit_price
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + quantity
                all_total_price = all_total_price + quantity * unit_price

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            flash("Product added to cart")
            return redirect(request.referrer)
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)


@app.route('/update_cart', methods=['POST'])
def update_product_cart():
    try:
        products_list = mongo.db.products
        quantity = int(request.form['quantity'])
        barcode = request.form['barcode']

        # validate the received values
        if quantity and barcode and request.method == 'POST':
            row = products_list.find_one({'barcode': barcode})

            unit_price = float('{:,.2f}'.format(row['price'] - row['price'] * row['discount'] / 100))

            itemArray = {

                row['barcode']: {'product_name': row['product_name'], 'barcode': row['barcode'], 'quantity': quantity,
                                 'price': unit_price, 'image': row['image'], 'total_price': quantity * unit_price}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:

                if row['barcode'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['barcode'] == key:
                            total_quantity = quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * unit_price
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + quantity
                all_total_price = all_total_price + quantity * unit_price

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            flash("Cart Updated")
            return redirect(request.referrer)
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)


@app.route('/empty')
def empty_cart():
    try:
        session.pop('cart_item')
        session.pop('all_total_quantity')
        session.pop('all_total_price')
        return redirect(url_for('products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:barcode>')
def delete_product(barcode):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == barcode:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@app.route('/store_locator/')
def store_locator():
    return render_template('Store_locator.html', title='Store Locator')


@app.route('/help/')
def help():
    return render_template('faq.html', title='Help')


@app.route('/checkout/', methods=["GET", "POST"])
def checkout():
    try:
        form = OrderForm()
        if request.method == "POST":
            if session['logged_in']:
                orders = mongo.db.orders
                card_number = form.card_number.data
                card_holder = form.card_holder.data
                expires = form.expires.data
                cvc = form.cvc.data
                hashed_card_number = bcrypt.hashpw(card_number.encode('utf-8'), bcrypt.gensalt())
                hashed_cvc = bcrypt.hashpw(cvc.encode('utf-8'), bcrypt.gensalt())
                now = datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                customer = session['email']
                name = form.name.data
                address = form.address.data
                city = form.city.data
                post_code = form.post_code.data
                phone_number = form.phone_number.data
                recipient_email = form.recipient_email.data
                ordered_products = []
                for value in session['cart_item'].items():
                    product_in_cart = {"barcode": value[1]["barcode"], "price": value[1]["price"],
                                       "quantity": value[1]["quantity"], "product_name": value[1]["product_name"]}
                    ordered_products.append(product_in_cart)

                orders.insert_one({'card_number': hashed_card_number, 'card_holder': card_holder, 'cvc': hashed_cvc,
                                   'expires': expires, 'order_date': formatted_date, 'customer': customer,
                                   'name': name, 'address': address, 'city': city, 'post_code': post_code,
                                   'phone_number': phone_number, 'email': recipient_email,
                                   'ordered_products': ordered_products})
                flash("Order Confirmed! Check your email for details")
                return redirect(url_for('products'))

            else:
                flash("Please login to continue")
                return redirect(url_for('login_customer'))

        return render_template('checkout.html', title='Checkout', form=form)

    except Exception as e:
        return str(e)


@app.route('/category/<selected>', methods=['GET'])
def category(selected):
    try:
        products_list = mongo.db.products
        all_products = products_list.find({"category": selected})
        all_categories = products_list.distinct("category")
        return render_template('products.html', title='Products', products=all_products, categories=all_categories)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.secret_key = 'mysecret'
    app.config["DEBUG"] = True
    app.run()


