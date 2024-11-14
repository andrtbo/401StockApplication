from flask import Flask, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from .extensions import db
from .models import *
from .forms import *
from .functions import *
import datetime

routes = Blueprint('routes', __name__)

# Variables 
# logged_in = False # Used to check if user is logged in. Change to "True" to access pages without logging in
# current_user = User() # User class to temporarily store the logged in user info
current_hours = MarketHours() # Define current_hours here so it can be used globally for a function
s_transactions = []

# Routes
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@routes.route("/", methods=["GET", "POST"]) # Login
def login():
    global current_user
    
    form = LoginForm()

    # What gets done when the current user submits
    if form.validate_on_submit():
        # Queries the information for the account with the specified username
        login_account = User.query.filter_by(username = form.username.data).first()
        
        try:
            # Checks if the form password matches the attempted account's password
            if check_password_hash(login_account.password, form.password.data):
                flash('Login successful.;green')
                
                # Sets the user as logged in and modifies the "current_user" object
                login_user(login_account)
                #logged_in = True
                #current_user = User.query.filter_by(username = form.username.data).first()
                return redirect(url_for('routes.portfolio'))
            else: 
                flash('The username or password is incorrect.;red')
        except AttributeError: # Flashes this message when an incorrect password causes an AttributeError
            flash('The username or password is incorrect.;red')

    return render_template('login.html', form=form)

@routes.route("/logout")
def logout():
    logout_user()
    flash('Logout successful.;green')
    return redirect(url_for('routes.login'))

@routes.route("/create-account", methods=["GET", "POST"])
def create_account():
    
    form = CreateForm()

    if form.validate_on_submit():
        # Creates a new_user object with form info
        new_user = User(
            username = form.username.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password = generate_password_hash(form.password.data, method='scrypt', salt_length=16),
            balance = 0,
            admin = False)
        
        uniqueness = test_unique(new_user) # Returns True only if the username and password aren't in the database already

        if uniqueness == True: 
            # Puts the new user into the database
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!;green')
            return redirect(url_for('routes.login'))
    
    return render_template('create_account.html', form=form)

@routes.route("/stocks", methods=["GET", "POST"]) 
@login_required
def stocks():
    form = SearchForm()
    return render_template('stocks.html', form=form)
    
@routes.route("/buy/<string:ticker>", methods=["GET", "POST"])
@login_required
def buy(ticker):
    update_stock()

    volume_form = TransactionForm()
    stock = Stock.query.filter_by(stock_ticker = ticker).first()
    current_hours = MarketHours.query.first() 
    modify_stock = OwnedStock.query.filter_by(id = current_user.id).filter_by(stock_ticker = ticker).first()

    if volume_form.validate_on_submit() and (check_hours(current_hours) == False):
        flash('Transactions unavailable outside of market hours.;red')
        return redirect(url_for('routes.portfolio'))
    elif volume_form.validate_on_submit():
        price = "{:.2f}".format(volume_form.stock_amount.data * stock.market_price)
        
        if current_user.balance > float(price): 
            try: 
                modify_stock.volume_owned = modify_stock.volume_owned + volume_form.stock_amount.data
            except AttributeError:
                modify_stock = OwnedStock(
                    id = current_user.id,
                    stock_ticker = ticker,
                    volume_owned = volume_form.stock_amount.data
                )
                db.session.add(modify_stock)

            modify_user = User.query.filter_by(id = current_user.id).first()
            modify_user.balance = modify_user.balance - float(price)
            stock.market_volume = stock.market_volume + volume_form.stock_amount.data
            
            record_transaction(ticker, volume_form.stock_amount.data, float(price), current_user)

            db.session.commit()
            flash(str(volume_form.stock_amount.data) + " " + ticker + " successfully purchased for $" + price + ".;green")
            return redirect(url_for('routes.portfolio'))
        else: 
            flash('Transaction failed due to insufficient balance.;red')

            try:
                volume_owned = modify_stock.volume_owned + 0
            except AttributeError:
                volume_owned = 0

            return render_template(
                'buy_page.html',
                ticker = ticker,
                volume_form = volume_form,
                stock = stock,
                balance = current_user.balance,
                volume_owned = volume_owned
            )

    try:
        volume_owned = modify_stock.volume_owned + 0
    except AttributeError:
        volume_owned = 0
    
    return render_template(
        'buy_page.html',
        ticker = ticker,
        volume_form = volume_form,
        stock = stock,
        balance = current_user.balance,
        volume_owned = volume_owned
    )

@routes.route("/sell/<string:ticker>", methods=["GET", "POST"]) # Same notes from /buy apply
@login_required
def sell(ticker):
    update_stock()

    volume_form = TransactionForm()
    stock = Stock.query.filter_by(stock_ticker = ticker).first()
    current_hours = MarketHours.query.first() 
    modify_stock = OwnedStock.query.filter_by(id = current_user.id).filter_by(stock_ticker = ticker).first()
    try:
        modify_stock.volume_owned = modify_stock.volume_owned + 0
    except AttributeError:
        modify_stock = OwnedStock(volume_owned = 0)

    if volume_form.validate_on_submit() and (check_hours(current_hours) == False):
        flash('Transactions unavailable outside of market hours.;red')
        return redirect(url_for('routes.portfolio'))
    elif volume_form.validate_on_submit():
        price = "{:.2f}".format(volume_form.stock_amount.data  * stock.market_price)
 
        if modify_stock.volume_owned >= volume_form.stock_amount.data:
            modify_stock = OwnedStock.query.filter_by(id = current_user.id).filter_by(stock_ticker = ticker).first()
            modify_stock.volume_owned = modify_stock.volume_owned - volume_form.stock_amount.data

            modify_user = User.query.filter_by(id = current_user.id).first()
            modify_user.balance = modify_user.balance + float(price)
            stock.market_volume = stock.market_volume - volume_form.stock_amount.data

            record_transaction(ticker, -volume_form.stock_amount.data, float(price), current_user)

            db.session.commit()
            flash(str(volume_form.stock_amount.data) + " " + ticker + " successfully sold for $" + price + ".;green")
            return redirect(url_for('routes.portfolio'))
        else: 
            flash('Transaction failed due to insufficient shares.;red')
            return render_template(
                'sell_page.html',
                ticker = ticker,
                volume_form = volume_form,
                stock = stock,
                balance = current_user.balance,
                volume_owned = modify_stock.volume_owned
            )

    try:
        volume_owned = modify_stock.volume_owned + 0
    except AttributeError:
        volume_owned = 0

    return render_template(
        'sell_page.html',
        ticker=ticker,
        volume_form=volume_form,
        stock = stock,
        balance = current_user.balance,
        volume_owned = volume_owned
    )

@routes.route("/portfolio")
@login_required
def portfolio():
    update_stock()

    portfolio = OwnedStock.query.\
        join(Stock, OwnedStock.stock_ticker == Stock.stock_ticker).\
        filter(OwnedStock.id == current_user.id).\
        add_columns(OwnedStock.stock_ticker, Stock.company_name, OwnedStock.volume_owned, Stock.market_price, Stock.market_volume).\
        order_by(OwnedStock.volume_owned).\
        all()

    return render_template(
        'portfolio.html',
        balance = current_user.balance,
        portfolio = portfolio
    )

@routes.route("/create_stock", methods=["GET", "POST"])
@login_required
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
            flash("Stock has successfully been added.;green")
            return redirect(url_for('routes.create_stock'))

    return render_template('create_stock.html', form=form)

@routes.route("/add_funds", methods=["GET", "POST"])
@login_required
def add_funds():
    form = AddFundsForm()

    if form.validate_on_submit() and form.deposit_amount.data > 0:  #Adjust later to fulfill database needs
        modify_user = User.query.filter_by(id = current_user.id).first()
        modify_user.balance = modify_user.balance + form.deposit_amount.data
        db.session.commit()

        flash('Funds Added Successfully!;green')
        return redirect(url_for('routes.portfolio'))
    elif form.validate_on_submit() and form.deposit_amount.data <= 0:
        flash('Deposit amount cannot be negative or zero.;green')

    return render_template(
        'add_funds.html',
        balance = current_user.balance,
        form=form
    )

@routes.route("/with_funds", methods=["GET", "POST"])
@login_required
def with_funds():
    form = WithFundsForm()

    if form.validate_on_submit() and form.withdraw_amount.data <= 0:
        flash('Withdrawal amount cannot be negative or zero.;red')
    elif form.validate_on_submit() and current_user.balance >= form.withdraw_amount.data:  #Adjust later to fulfill database needs
        modify_user = User.query.filter_by(id = current_user.id).first()
        modify_user.balance = modify_user.balance - form.withdraw_amount.data
        db.session.commit()

        flash('Funds Withdrawn Successfully!;green')
        return redirect(url_for('routes.portfolio'))
    elif form.validate_on_submit() and current_user.balance < form.withdraw_amount.data:
        flash('Insufficient balance.;red')
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
@login_required
def market():
    global current_hours
    current_hours = MarketHours.query.first() # There's only one time in the market_hours table so this is fine
    form = MarketForm( # Set the default select fields to be the current market hours
        start_time = current_hours.start_time[:-6],
        XM_1 = current_hours.start_time[-2:],
        end_time = current_hours.end_time[:-6],
        XM_2 = current_hours.end_time[-2:],
        start_day = current_hours.start_day,
        end_day = current_hours.end_day
    )
    
    if form.validate_on_submit():  
        # Assembles strings for the start/end times
        start_time = str(form.start_time.data + ":00 " + form.XM_1.data)
        end_time = str(form.end_time.data + ":00 " + form.XM_2.data)

        # Validates that the start time is before the end time
        if time_conv(start_time) > time_conv(end_time):
            flash('Start time cannot be after end time.;red')
            return render_template('market.html', form=form, current_hours=current_hours)
        else:
            flash('Market hours updated successfully.;green')

        # Store the new times/days in the database
        current_hours.start_time = start_time
        current_hours.end_time = end_time
        current_hours.start_day = form.start_day.data
        current_hours.end_day = form.end_day.data
        db.session.commit()

        return render_template('market.html', form=form, current_hours=current_hours)
    
    return render_template('market.html', form=form, current_hours=current_hours)

@routes.route("/transaction_history/<int:page>", methods=["GET", "POST"]) 
@login_required
def trans_history(page):
    global s_transactions
    form = SearchForm()

    # Code for displaying all transactions
    transactions = Transactions.query.\
        join(Stock, Transactions.stock_ticker == Stock.stock_ticker).\
        filter(Transactions.id == current_user.id).\
        add_columns(Transactions.transaction_id, Transactions.stock_ticker, Transactions.purchase_price, Transactions.purchase_volume, Transactions.transaction_time, Stock.company_name).\
        order_by(Transactions.transaction_id).\
        all()
    transactions.reverse()

    page_count, page_transactions = paginate(transactions, page)

    # If a search is made
    if form.validate_on_submit():
        s_transactions = []

        for transaction in transactions:
            if (form.search.data.lower() in transaction.stock_ticker.lower()) or (form.search.data.lower() in transaction.company_name.lower()):
                s_transactions.append(transaction)

        page_count, page_transactions = paginate(s_transactions, page)
        
        return render_template(
            'trans_history.html',
            transactions = page_transactions,
            page = page,
            page_count = page_count,
            form = form
        )

    try:
        s_transactions[0]
        page_count, page_transactions = paginate(s_transactions, page)

        return render_template(
            'trans_history.html',
            transactions = page_transactions,
            page = page,
            page_count = page_count,
            form = form
        )
    except IndexError:
        return render_template(
            'trans_history.html',
            transactions = page_transactions,
            page = page,
            page_count = page_count,
            form = form
        )