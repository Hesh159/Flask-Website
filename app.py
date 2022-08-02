from flask import Flask, render_template, session, redirect, url_for, g, request, Response
from database import get_db, close_db
from forms import RegistrationForm, LoginForm, StockAmountForm, ReviewForm, ProductEditForm, StockEditForm, NewProductForm, NewAdminForm, changePasswordForm, TokenForm, NewPasswordForm, contactForm, CheckoutForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import smtplib
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature

app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'verysecretkey'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

s = URLSafeTimedSerializer('extremelysecretkey')

#!!!NOTES ON THE WEBSITE!!!#
''' 
There are both regular users and admins, I have kindly created an admin account in advance for you, the username is REDACTED and the
password is ihatewombats . Regular users can do the typical things you would expect, admins can create new admins, update and change product info,
add new products, and the like. If you want to use a regular account there is one with the username James19 and the password is password123 
(james is not very intelligent.) 
If a regular user attempts to access an admin only page, they will be logged out of their account, this effective and irritating method of 
defense rivals the likes of microsoft.
All code on the website is mine unless explicitly stated otherwise, exept for the things I got from your lectures
'''

@app.teardown_appcontext
def close_db_at_end_of_request(e=None):
    close_db()

@app.before_request
def load_load_loggen_in_user():
    g.user = session.get('user_id', None)

@app.before_request
def load_load_loggen_in_user():
    g.admin = session.get('is_admin', None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index2():
    return render_template('index.html')


#account registration 
#requires a unique username, password of at least 8 characters, and an email
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data 
        user_id = user_id.strip()
        password = form.password.data 
        password2 = form.password2.data
        email = form.email.data

        db = get_db()
        if db.execute(""" SELECT * FROM users                  
                          WHERE user_id = ?""", (user_id,)).fetchone() is not None:
            form.user_id.errors.append('There already exists a user with this id')
        elif db.execute(""" SELECT * FROM users                  
                        WHERE email = ?""", (email,)).fetchone() is not None:
            form.email.errors.append('This email is already in use')
        else:
            db.execute("""INSERT INTO users (user_id, password, email)
                    VALUES (?, ?, ?);""", (user_id, generate_password_hash(password), email))
            db.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form = form)

#login
#login form, allows both admins and normal users to log in, probably not very efficient
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()

        admin_check = db.execute("""SELECT * FROM admins WHERE admin_id = ?""", (user_id,)).fetchone()
        if admin_check is not None:
            if check_password_hash(admin_check['password'], password):
                    session.clear()
                    session['is_admin'] = user_id 
                    session['user_id'] = user_id
                    return render_template('admin_main.html')

        user = db.execute(''' SELECT * FROM users WHERE user_id = ?;''', (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append('Unknown user id')
        elif not check_password_hash(user['password'], password):
            form.password.errors.append('Incorrect password!')
        else:
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('index'))
    return render_template('login.html', form = form)

#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#change password part 1
'''uses the smtp library, I got most of the smtp stuff from the book 'Automate the boring stuff with pyton' by Al Sweigart
creating the token took a lot of broswing the itsdangerous documentation and I also referenced the following video
https://www.youtube.com/watch?v=vF9n248M1yk
unfortunately this does not run on the ucc server, however it runs on my local server and I would be happy to provide evidence of it working in
the form of a video or something idk
'''
@app.route('/change_password', methods=['GET','POST'])
def change_password():
    form = changePasswordForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        email = form.email.data

        db = get_db()
        user = db.execute(''' SELECT * FROM users WHERE user_id = ?;''', (user_id,)).fetchone()
        email_check = db.execute("""SELECT email FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append('Unknown user id')
        elif email_check[0] != email:
            form.email.errors.append('Incorrect email!')
        else:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.ehlo()
            smtpObj.login('cpunter123@gmail.com', 'darragh123')

            reset_token = s.dumps(email, salt='reset')

            db.execute("""UPDATE users SET token = ? WHERE user_id = ?;""", (True,user_id))
            db.commit()
            
            smtpObj.sendmail('cpunter123@gmail.com', email, 'Subject\nReset token: (copy this and paste it in the next appropriate field)    ' + reset_token)
            smtpObj.quit()
            return redirect( url_for('token_confirm', user_id = user_id))
    return render_template('change_password.html', form = form)

#change password part 2
'''
This part requires you copy the token that is sent to your email into the form, if its valid you proceed to the final part of the password
changing process
'''
@app.route('/token_confirm/<user_id>', methods=['GET', 'POST'])
def token_confirm(user_id):
    form = TokenForm()
    if form.validate_on_submit():
        token = form.token.data
        return redirect (url_for('new_password', token = token, user_id = user_id ))
    return render_template('token_confirm.html', form = form)

#change password part 3
'''
This part contains the actual password changing process, as well as an attempt at avoiding users using the same token multiple times.
From a stackoverflow post I got the idea to add a part to the users database that tells if the user has a token currently. I only got the 
idea, no code was provided in the post, I guess the idea itself is a significant portion of the work though. 
In theory the database is updated to true for the user in the step one, in this part it makes sure the token isn't set to false
and after the password change is finished the token is set to false. However this isn't tested properly and I couldn't really get it to work.
The rest of the password changing process works fine.
'''
@app.route('/new_password/<token>/<user_id>', methods=['GET','POST'])
def new_password(token, user_id):
    form = None
    db = get_db()
    if db.execute("""SELECT token FROM users WHERE user_id = ?;""", (user_id,)).fetchone() == False:
        return render_template ('new_password.html', form = form, error= 'Token already used')
    try:
        reset_token = s.loads(token, max_age=900, salt='reset')
    except BadSignature as e:
        return render_template ('new_password.html', form = form, error= 'Token expired, was incorrect, or was tapered with') 
    form = NewPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        db = get_db()
        db.execute("""UPDATE users SET password = ? WHERE user_id = ?;""",(generate_password_hash(password), user_id))
        db.commit()
        db.execute("""UPDATE users SET token = False WHERE user_id = ?;""", (user_id,))
        db.commit()
        return redirect(url_for('login'))
    return render_template('new_password.html', error = '', form = form)


#store
#shows all ware
@app.route('/browse')
def browse():
    db = get_db()
    items = db.execute("""SELECT item, price, item_id FROM items;""").fetchall()
    return render_template('browse.html', item = items)

#individual items
#shows each item in further detail, users can use the form to specify how much of the item they would like to add to their cart
#items are removed from database while in the cart
#also shows the average rating of the user reviews and how many reviews there are
@app.route('/item/<int:item_id>', methods = ['GET', 'POST'])
def item(item_id):
    db = get_db()
    item = db.execute(""" SELECT * from items 
                        where item_id = ?;""", (item_id,)).fetchone()
    stock = ''
    stock_check = db.execute("""SELECT stock FROM items WHERE item_id = ?;""",(item_id,)).fetchone()
    if stock_check[0] == 0:
        stock = 'Out of stock'

    totalReviews = db.execute("""SELECT count(review_number) FROM reviews WHERE item_id = ?;""",(item_id,)).fetchone()
    avg_score = db.execute("""select avg(rating) from reviews where item_id = ?;""", (item_id,)).fetchone()

    form = StockAmountForm()
    choice = []
    for num in range(1, stock_check[0] + 1):
        choice.append((num, num))
    form.amount.choices = choice

    if form.validate_on_submit():
        if g.user is None:
            return redirect(url_for('login'))
        amount = form.amount.data
        db.execute("""UPDATE items
                        SET stock = stock - ?
                        WHERE item_id = ?;""", (amount, item_id))
        db.commit()
        return redirect( url_for('add_to_cart', item_id = item_id, amount = amount))
    return render_template('item.html', item = item, stock = stock, form = form, score = avg_score[0], total = totalReviews[0])

#cart
#Displays all items in the users cart, the price of each item, and the total price of everything in the cart
@app.route('/cart')
def cart():
    if g.user is None:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = {}
    names = {}
    prices = {}
    db = get_db()
    total = 0
    price = ''
    for item_id in session['cart']:
        name = db.execute(""" select * from items where item_id = ?;""", (item_id,)).fetchone()['item']
        names[item_id] = name
        price = db.execute("""SELECT price FROM items WHERE item_id = ?;""", (item_id,)).fetchone()
        price = session['cart'][item_id] * price[0]
        total = total + price
        price = f'€{price}'
        prices[item_id] = price
    total = round(total, 2)
    return render_template('cart.html', cart = session['cart'], names = names, price = prices, total = total, message = '')

#Adds items to the users cart
@app.route('/add_to_cart/<int:item_id>/<int:amount>')
def add_to_cart(item_id, amount):
    if g.user is None:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = {}
    if item_id not in session['cart']:
        session['cart'][item_id] = 0
    session['cart'][item_id] = session['cart'][item_id] + amount
    return redirect( url_for('cart') )

#Allows users to remove items from their carts, updates the database to reflect the items being available again
@app.route('/remove_from_cart/<int:item_id>/<int:amount>')
def remove_from_cart(item_id, amount):
    session['cart'].pop(item_id)
    db = get_db()
    db.execute("""UPDATE items
                        SET stock = stock + ?
                        WHERE item_id = ?;""", (amount, item_id))
    db.commit()
    return redirect (url_for('cart'))


#checkout
'''
very rough, and with no way to add money to the accounts youre gonna have to use the default values in there 
'''
@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if g.user is None:
        return redirect(url_for('login'))
    form = CheckoutForm()
    names = {}
    prices = {}
    all_items = ' '
    db = get_db()
    total = 0
    user_id = session['user_id']
    price = ''
    for item_id in session['cart']:
        name = db.execute(""" select * from items where item_id = ?;""", (item_id,)).fetchone()['item']
        names[item_id] = name
        price = db.execute("""SELECT price FROM items WHERE item_id = ?;""", (item_id,)).fetchone()
        price = session['cart'][item_id] * price[0]
        total = total + price
        price = f'€{price}'
        prices[item_id] = price
        all_items = all_items + name
    total = round(total, 2)
    if form.validate_on_submit():
        address = form.address.data
        money = db.execute("""SELECT money FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if money[0] - total < 0:
            return render_template('checkout.html', form = form, error = 'You dont have enough money in your account for this')
        else:
            new_balance = money[0] - total
            db.execute("""UPDATE users SET money = ? WHERE user_id = ?;""", (new_balance, user_id))
            db.commit()
            session['cart'] = {}
            db.execute("""INSERT INTO orders (user_id, address, items) VALUES (?,?,? );""",(user_id, address, all_items))
            db.commit()
            return render_template('cart.html',cart = session['cart'], names = None, price = None, total = None, message = 'Thank you for your purchase')
    return render_template('checkout.html',cart = session['cart'], names = names, price = prices, total = total, form = form, error = 'error' )
            



#reviews
#create a review
@app.route('/review/<int:item_id>', methods= ['GET', 'POST'])
def review(item_id):
    if g.user is None:
        return redirect(url_for('login'))
    form = ReviewForm()
    if form.validate_on_submit():
        rating = form.rating.data
        review = form.review.data
        db = get_db()
        db.execute("""INSERT INTO reviews (item_id, user_id, rating, review)
                    VALUES (?, ?, ?, ?);""", (item_id, session['user_id'], rating, review))
        db.commit()
        return redirect( url_for('reviews',item_id = item_id))
    return render_template('review.html', form = form)


#view reviews
@app.route('/reviews/<int:item_id>')
def reviews(item_id):
    db = get_db()
    reviews = db.execute("""SELECT * FROM reviews WHERE item_id = ?;""", (item_id, )).fetchall()
    item = db.execute(""" SELECT * from items where item_id = ?;""", (item_id,)).fetchone()
    totalReviews = db.execute("""SELECT count(review_number) FROM reviews WHERE item_id = ?;""",(item_id,)).fetchone()
    return render_template('reviews.html', reviews = reviews, item = item, total = totalReviews[0])

#send suggestions etc to the admins
@app.route('/contact', methods=['GET','POST'])
def contact():
    if g.user is None:
        return redirect(url_for('login'))
    form = contactForm()
    if form.validate_on_submit():
        suggestion = form.suggestion.data
        db = get_db()
        db.execute("""INSERT INTO suggestions (user_id, suggestion) VALUES (?, ?);""", (session['user_id'], suggestion))
        db.commit()
        return redirect(url_for('index'))
    return render_template('contact.html', form = form)

#admin stuff
#these are accessible after logging in as an admin

#view all products
@app.route('/products')
def products():
    if g.admin is None:
        return redirect(url_for('logout'))
    db = get_db()
    products = db.execute("""SELECT * FROM items""").fetchall()
    return render_template('products.html', items = products)

#edit products
#allows admins to edit each products name, price, or description
@app.route('/product_edit/<int:item_id>', methods= ['GET', 'POST'])
def product_edit(item_id):
    if g.admin is None:
        return redirect(url_for('logout'))

    form = ProductEditForm()
    db = get_db()
    previous_info = db.execute("""SELECT * FROM items WHERE item_id = ?;""", (item_id,)).fetchone()

    if form.validate_on_submit():
        newName = form.newName.data
        newPrice = form.newPrice.data 
        newDescription = form.newDescription.data

        db.execute("""UPDATE items SET item = ?, price = ?, description = ? WHERE item_id = ?;""", (newName, newPrice, newDescription, item_id))
        db.commit()
        return redirect( url_for('products'))
    return render_template('product_edit.html', form = form, previous = previous_info, item_id = item_id)

#edit stock
#allows admins to increase or decrease the stock of each item
@app.route('/stock_edit/<int:item_id>', methods= ['GET', 'POST'])
def stock_edit(item_id):
    if g.admin is None:
        return redirect(url_for('logout'))

    form = StockEditForm()
    db = get_db()
    name = db.execute("""SELECT item, stock FROM items WHERE item_id = ?""", (item_id,)).fetchone()

    if form.validate_on_submit():
        stockEdit = form.stockEdit.data
  
        if name[1] + stockEdit < 0:
            return render_template('stock_edit.html', form = form, name = name, error = 'Error: cannot have negative stock')

        db.execute("""UPDATE items SET stock = stock + ? WHERE item_id = ?""", (stockEdit, item_id))
        db.commit()
        return redirect( url_for('products'))
    return render_template('stock_edit.html', form = form, name = name, error = '')

#allows admins to create new products to sell
@app.route('/new_product', methods= ['GET', 'POST'])
def new_product():
    if g.admin is None:
        return redirect(url_for('logout'))
    
    form = NewProductForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        stock = form.stock.data
        description = form.description.data

        db = get_db()
        db.execute("""INSERT INTO items (item, price, stock, description)
                    VALUES (?, ?, ?, ?);""", (name, price, stock, description))
        db.commit()
        return redirect ( url_for('products'))
    return render_template('new_product.html', form = form)

#allows admins to delete a product, use with caution
@app.route('/delete_product/<int:item_id>')
def delete_product(item_id):
    if g.admin is None:
        return redirect(url_for('logout'))

    db = get_db()
    db.execute("""DELETE FROM items WHERE item_id = ?;""", (item_id,))
    db.commit()
    return redirect (url_for('products'))

#allows admins to add a new admin account
@app.route('/new_admin', methods= ['GET', 'POST'])
def new_admin():
    if g.admin is None:
        return redirect(url_for('logout'))
    form = NewAdminForm()
    if form.validate_on_submit():
        admin_id = form.admin_id.data 
        admin_id = admin_id.strip()
        password = form.password.data 
        password2 = form.password2.data

        db = get_db()
        if db.execute(""" SELECT * FROM admins                  
                          WHERE admin_id = ?""", (admin_id,)).fetchone() is not None:
            form.admin_id.errors.append('There already exists an admin with this id')
        else:
            db.execute("""INSERT INTO admins (admin_id, password)
                    VALUES (?, ?);""", (admin_id, generate_password_hash(password)))
            db.commit()
            return render_template('admin_main.html')
    return render_template('new_admin.html', form = form)

#lets admins return to the admin page
@app.route('/adminview')
def adminview():
    if g.admin is None:
        return redirect(url_for('logout'))
    return render_template('admin_main.html')

#view user suggestions
@app.route('/view_suggestions')
def view_suggestions():
    if g.admin is None:
        return redirect(url_for('logout'))
    db = get_db()
    suggestions = db.execute("""SELECT * FROM suggestions;""")
    return render_template('suggestions.html', suggestions = suggestions)
