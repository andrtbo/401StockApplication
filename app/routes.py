from flask import Flask, render_template, redirect, url_for, flash, Blueprint
from .extensions import db
from .models import *
from .forms import *
import datetime

routes = Blueprint('routes', __name__)

# Variables 
logged_in = False # Used to check if user is logged in. Change to "True" to access pages without logging in
current_user = User() # User class to temporarily store the logged in user info

# Functions
def test_unique(input_user): # Checks to see if a created account's username or password are unique 
    try: 
        test_user = User.query.filter_by(username = input_user.username).first()
        if test_user.username == input_user.username:
            flash("This username is already in use.")
            return False
    except AttributeError:
        try:
            test_user = User.query.filter_by(email = input_user.email).first()
            if test_user.email == input_user.email:
                flash("This email is already in use.")
                return False
        except AttributeError:
            return True

def unique_stock(input_stock):
    try:
        test_stock = Stock.query.filter_by(stock_ticker = input_stock.stock_ticker).first()
        if test_stock.stock_ticker == input_stock.stock_ticker:
            flash("This stock ticker is already in use.")
            return False
    except AttributeError:
        try:
            test_stock = Stock.query.filter_by(company_name = input_stock.company_name).first()
            if test_stock.company_name == input_stock.company_name:
                flash("The company name is already in use.")
                return False
        except AttributeError:
            return True

def record_transaction(ticker, volume, price):
    timestamp = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")

    new_transaction = Transactions(
        user_id = current_user.user_id,
        stock_ticker = ticker,
        purchase_price = price,
        purchase_volume = volume,
        transaction_time = timestamp
    )

    db.session.add(new_transaction)

# Routes
@routes.route("/dashboard")
def dashboard():
    global logged_in # Makes sure all functions are accessing/editing the same "logged_in" variable

    if not logged_in: # I'd rather a function than using an if else for everything, but the redirect works weirdly otherwise
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('routes.login'))
    else:
        return render_template('dashboard.html')

@routes.route("/", methods=["GET", "POST"])
def login():
    global current_user
    global logged_in
    form = LoginForm()

    # What gets done when the current user submits
    if form.validate_on_submit():
        # Queries the information for the account with the specified username
        login_account = User.query.filter_by(username = form.username.data).first()
        
        try:
            # Checks if the form password matches the attempted account's password
            if login_account.password == form.password.data:
                flash('Login successful')
                
                # Sets the user as logged in and modifies the "current_user" object
                logged_in = True
                current_user = User.query.filter_by(username = form.username.data).first()
                return redirect(url_for('routes.portfolio'))
            else: 
                flash('The username or password is incorrect.')
        except AttributeError: # Flashes this message when an incorrect password causes an AttributeError
            flash('The username or password is incorrect.')

    return render_template('login.html', form=form)

@routes.route("/logout")
def logout():
    global logged_in
    global current_user

    # Sets the logged_in variable to false and makes the current_user variable blank
    logged_in = False
    current_user = User()

    return redirect(url_for('routes.login'))

@routes.route("/create-account", methods=["GET", "POST"])
def create_account():
    global logged_in
    form = CreateForm()

    if form.validate_on_submit():
        # Creates a new_user object with form info
        new_user = User(
            username = form.username.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password = form.password.data,
            balance = 0,
            admin = False)
        
        uniqueness = test_unique(new_user) # Returns True only if the username and password aren't in the database already

        if uniqueness == True: 
            # Puts the new user into the database
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!')
            return redirect(url_for('routes.login'))
    
    return render_template('create_account.html', form=form)

@routes.route("/stocks", methods=["GET", "POST"]) 
def stocks():
    global logged_in

    # Return to the login page if not logged in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('routes.login'))
    else:
        form = SearchForm()

        return render_template('stocks.html', form=form)
    
@routes.route("/buy/<string:ticker>", methods=["GET", "POST"])
def buy(ticker):
    volume_form = TransactionForm()
    stock = Stock.query.filter_by(stock_ticker = ticker).first()

    # The form.submit.data conditional is needed so the forms don't submit each other
    if volume_form.validate_on_submit(): # Re-renders the page with updated form data value
        price = float("{:.2f}".format(volume_form.stock_amount.data * stock.market_price))
        
        if current_user.balance > price: 
            modify_stock = OwnedStock.query.filter_by(user_id = current_user.user_id).filter_by(stock_ticker = ticker).first()
            try: 
                modify_stock.volume_owned = modify_stock.volume_owned + volume_form.stock_amount.data
            except AttributeError:
                modify_stock = OwnedStock(
                    user_id = current_user.user_id,
                    stock_ticker = ticker,
                    volume_owned = volume_form.stock_amount.data
                )
                db.session.add(modify_stock)

            modify_user = User.query.filter_by(user_id = current_user.user_id).first()
            modify_user.balance = modify_user.balance - price
            
            record_transaction(ticker, volume_form.stock_amount.data, price)

            db.session.commit()
            flash(str(volume_form.stock_amount.data) + " " + ticker + " successfully purchased for $" + str(price) + ".")
            return redirect(url_for('routes.portfolio'))
        else: 
            flash('Transaction failed due to insufficient balance.')
            return render_template(
                'buy_page.html',
                ticker = ticker,
                volume_form = volume_form,
                price = stock.market_price,
                balance = current_user.balance
            )

    return render_template(
        'buy_page.html',
        ticker = ticker,
        volume_form = volume_form,
        price = stock.market_price,
        balance = current_user.balance
    )

@routes.route("/sell/<string:ticker>", methods=["GET", "POST"]) # Same notes from /buy apply
def sell(ticker):
    volume_form = TransactionForm()

    # The form.submit.data conditional is needed so the forms don't submit each other
    if volume_form.validate_on_submit(): # Re-renders the page with updated form data value
        price = "{:.2f}".format(volume_form.stock_amount.data)
        flash(str(volume_form.stock_amount.data) + " " + ticker + " successfully sold for $" + str(price) + ".")
        return redirect(url_for('routes.portfolio'))

    return render_template(
        'sell_page.html',
        ticker=ticker,
        volume_form=volume_form
    )

@routes.route("/portfolio")
def portfolio():
    global logged_in
    global current_user

    current_user = User.query.filter_by(user_id = current_user.user_id).first()

    # Return to the login page if not logged in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('routes.login'))
    else:
        return render_template(
            'portfolio.html',
            balance = current_user.balance
        )

@routes.route("/load-db")
def load_db():    
    db.create_all()
    flash('DB Created')
    return render_template('dashboard.html')

@routes.route("/create_stock", methods=["GET", "POST"])
def create_stock():
    form = StockForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        new_stock = Stock(
            stock_ticker = form.stock_ticker.data,
            company_name = form.company_name.data,
            market_price = form.market_price.data,
            market_volume = form.market_volume.data
        )
    
        uniqueness = unique_stock(new_stock)

        if uniqueness == True:
            db.session.add(new_stock)
            db.session.commit()
            flash("Stock has successfully been added.")
            return redirect(url_for('routes.create_stock'))

    return render_template('create_stock.html', form=form)

@routes.route("/add_funds", methods=["GET", "POST"])
def add_funds():
    form = AddFundsForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        modify_user = User.query.filter_by(user_id = current_user.user_id).first()
        modify_user.balance = modify_user.balance + form.deposit_amount.data
        db.session.commit()

        flash('Funds Added Successfully!')
        return redirect(url_for('routes.portfolio'))

    return render_template(
        'add_funds.html',
        balance = current_user.balance,
        form=form
    )

@routes.route("/with_funds", methods=["GET", "POST"])
def with_funds():
    form = WithFundsForm()

    if form.validate_on_submit() and current_user.balance >= form.withdraw_amount.data:  #Adjust later to fulfill database needs
        modify_user = User.query.filter_by(user_id = current_user.user_id).first()
        modify_user.balance = modify_user.balance - form.withdraw_amount.data
        db.session.commit()

        flash('Funds Withdrawn Successfully!')
        return redirect(url_for('routes.portfolio'))
    elif form.validate_on_submit():
        flash('Insufficient balance.')
        return render_template(
            'with_funds.html',
            balance = current_user.balance,
            form = form
        )

    return render_template(
        'with_funds.html',
        balance = current_user.balance,
        form = form
    )

@routes.route("/market", methods=["GET", "POST"])
def market(): 
    form = MarketHours()
    
    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('The market hours have been adjusted')
        return redirect(url_for('routes.market'))

    new_hours = MarketHours(start_time = form.start_time.data, end_time = form.end_time.data, start_day = form.start_day.data, end_day = form.end_day.data)

    return render_template('market.html', form=form)

@routes.route("/trans_history", methods=["GET", "POST"]) #Adjust later for database
def trans_history():
    transactions = Transactions.query.filter_by(user_id = current_user.user_id).all()
    transactions.reverse()

    return render_template('trans_history.html', transactions = transactions)