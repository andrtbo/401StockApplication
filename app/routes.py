from flask import Flask, render_template, redirect, url_for, flash, Blueprint
from .extensions import db
from .models import *
from .forms import *

routes = Blueprint('routes', __name__)

# Variables 
logged_in = True # Used to check if user is logged in. Change to "True" to access pages without logging in
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

# Routes
@routes.route("/dashboard")
def dashboard():
    global logged_in # Makes sure all functions are accessing/editing the same "logged_in" variable

    if not logged_in: # I'd rather a function than using an if else for everything, but the redirect works weirdly otherwise
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('routes.login'))
    else:
        return render_template('dashboard.html')

@routes.route("/login", methods=["GET", "POST"])
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
                current_user = User(username = login_account.username, first_name = login_account.first_name, last_name = login_account.last_name, email = login_account.email, password = login_account.password, admin = login_account.admin)
                return redirect(url_for('routes.dashboard'))
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
        new_user = User(username = form.username.data, first_name = form.first_name.data, last_name = form.last_name.data, email = form.email.data, password = form.password.data, admin = False)
        
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
    volume_form = TradeInput()
    submit_form = ConfirmPurchase()

    # The form.submit.data conditional is needed so the forms don't submit each other
    if volume_form.submit.data and volume_form.validate_on_submit(): # Re-renders the page with updated form data value
        return render_template('buy_page.html', ticker=ticker, volume_form=volume_form, submit_form=submit_form)
    elif volume_form.submit.data and submit_form.validate_on_submit(): # Actually submits the form
        flash('Stock purchased successfully! Visit transaction history to view.')
        return redirect(url_for('routes.dashboard'))

    return render_template('buy_page.html', ticker=ticker, volume_form=volume_form, submit_form=submit_form)

@routes.route("/sell/<string:ticker>", methods=["GET", "POST"]) # Same notes from /buy apply
def sell(ticker):
    volume_form = TradeInput()
    submit_form = ConfirmPurchase()

    if volume_form.submit.data and volume_form.validate_on_submit(): 
        return render_template('sell_page.html', ticker=ticker, volume_form=volume_form, submit_form=submit_form)

    if submit_form.submit.data and submit_form.validate_on_submit():
        flash('Stock sold successfully! Visit transaction history to view.')
        return redirect(url_for('routes.dashboard'))

    return render_template('sell_page.html', ticker=ticker, volume_form=volume_form, submit_form=submit_form)

@routes.route("/")
def portfolio():
    global logged_in

    # Return to the login page if not logged in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('routes.login'))
    else:
        return render_template('portfolio.html')

@routes.route("/load-db")
def load_db():    
    db.create_all()
    flash('DB Created')
    return render_template('dashboard.html')

@routes.route("/create_stock", methods=["GET", "POST"])
def create_stock():

    form = StockForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Stock Has Been Added to the Market!')
        return redirect(url_for('routes.create_stock'))

    new_stock = Stock(stock_ticker = form.stock_ticker.data, company_name = form.company_name.data, market_price = form.market_price.data, volume_owned = form.volume_owned.data, market_volume = form.market_volume.data)
    
    return render_template('create_stock.html', form=form)

@routes.route("/add_funds", methods=["GET", "POST"])
def add_funds():

    form = AddFundsForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Funds Added Successfully!')
        return redirect(url_for('routes.add_funds'))

    return render_template('add_funds.html', form=form)

@routes.route("/with_funds", methods=["GET", "POST"])
def with_funds():

    form = WithFundsForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Funds Withdrawn Successfully!')
        return redirect(url_for('routes.with_funds'))

    return render_template('with_funds.html', form=form)

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

    return render_template('trans_history.html')