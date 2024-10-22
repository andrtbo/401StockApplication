from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp_key' #Change key later
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['WTF_CSRF_ENABLED'] = False

# Classes for databases
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(255))
    admin = db.Column(db.Boolean)

class Stock(db.Model):
    stock_ticker = db.Column(db.String(5), primary_key=True)
    company_name = db.Column(db.String(255))
    market_price = db.Column(db.Float, nullable = False)
    volume_owned = db.Column(db.Integer)
    market_volume = db.Column(db.Integer)

class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    total_balance = db.Column(db.Float)
    cash_balance = db.Column(db.Float)  

class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    purchase_price = db.Column(db.Float)
    purchase_volume = db.Column(db.Integer)

class MarketHours(db.Model):
    start_time = db.Column(db.Integer, primary_key=True)
    end_time = db.Column(db.Integer)
    start_day = db.Column(db.String)
    end_day = db.Column(db.String)

# Classes for forms
class CreateForm(FlaskForm): #Form with fields required for logging in
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm): #Form with fields required for logging in
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class StockForm(FlaskForm): #Form to add the stock to DB
    stock_ticker = StringField('Stock Ticker', validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    market_price = FloatField('Market Price', validators=[DataRequired()])
    volume_owned = IntegerField('Volume Owned', validators=[DataRequired()])
    market_volume = IntegerField('Market Volume', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class AddFundsForm(FlaskForm): #Form to add funds to account
    deposit_amount = IntegerField('Deposit Amount', validators=[DataRequired()])
    bank_number = IntegerField('Bank Account Number', validators=[DataRequired()])
    submit = SubmitField('Add Funds')

class WithFundsForm(FlaskForm): #Form to withdrawal funds from account
    withdraw_amount = IntegerField('Withdraw Amount', validators=[DataRequired()])
    submit = SubmitField('Withdraw Funds')

class MarketHours(FlaskForm): #Form to set market hours for application
    start_time = IntegerField('Start Time (1-24)', validators = [DataRequired()])
    end_time = IntegerField('End Time (1-24)', validators = [DataRequired()])
    start_day = StringField('Start Day', validators = [DataRequired()])
    end_day = StringField('End Day', validators = [DataRequired()])

class TradeInput(FlaskForm): # Form for inputting the amount of stock to buy/sell
    stock_amount = IntegerField('How many stocks would you like to purchase?', validators=[DataRequired()])
    submit = SubmitField('Calculate total')

class ConfirmPurchase(FlaskForm):
    submit = SubmitField('Purchase')

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

@app.route("/dashboard")
def dashboard():
    global logged_in # Makes sure all functions are accessing/editing the same "logged_in" variable

    if not logged_in: # I'd rather a function than using an if else for everything, but the redirect works weirdly otherwise
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        return render_template('dashboard.html')

@app.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for('dashboard'))
            else: 
                flash('The username or password is incorrect.')
        except AttributeError: # Flashes this message when an incorrect password causes an AttributeError
            flash('The username or password is incorrect.')

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    global logged_in
    global current_user

    # Sets the logged_in variable to false and makes the current_user variable blank
    logged_in = False
    current_user = User()

    return redirect(url_for('login'))

@app.route("/create-account", methods=["GET", "POST"])
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
            return redirect(url_for('login'))
    
    return render_template('create_account.html', form=form)

@app.route("/stocks", methods=["GET", "POST"]) 
def stocks():
    global logged_in

    # Return to the login page if not logged in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        form = SearchForm()

        return render_template('stocks.html', form=form)
    
@app.route("/buy/<string:ticker>", methods=["GET", "POST"])
def buy(ticker):
    price = 0.0
    form = TradeInput()
    form2 = ConfirmPurchase()

    if form.validate_on_submit():
        price = "{:.2f}".format(float(form.stock_amount.data) * 5.03, 2)
        return render_template('buy_page.html', ticker=ticker, form=form, form2=form2, price=str(price))

    if form2.validate_on_submit():
        flash('Stock purchased successfully! Visit transaction history to view.')
        return redirect(url_for('dashboard'))

    return render_template('buy_page.html', ticker=ticker, form=form, form2=form2, price=price)

@app.route("/sell/<string:ticker>", methods=["GET", "POST"])
def sell(ticker):
    price = 0.0
    form = TradeInput()
    form2 = ConfirmPurchase()

    if form.validate_on_submit():
        price = "{:.2f}".format(float(form.stock_amount.data) * 5.03, 2)
        return render_template('sell_page.html', ticker=ticker, form=form, form2=form2, price=str(price))

    if form2.validate_on_submit():
        flash('Stock sold successfully! Visit transaction history to view.')
        return redirect(url_for('dashboard'))

    return render_template('sell_page.html', ticker=ticker, form=form, form2=form2, price=price)

@app.route("/")
def portfolio():
    db.create_all()
    global logged_in

    # Return to the login page if not logged in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        return render_template('portfolio.html')
    
@app.route("/create_stock", methods=["GET", "POST"])
def create_stock():

    form = StockForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Stock Has Been Added to the Market!')
        return redirect(url_for('create_stock'))

    new_stock = Stock(stock_ticker = form.stock_ticker.data, company_name = form.company_name.data, market_price = form.market_price.data, volume_owned = form.volume_owned.data, market_volume = form.market_volume.data)
    
    return render_template('create_stock.html', form=form)

@app.route("/add_funds", methods=["GET", "POST"])
def add_funds():

    form = AddFundsForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Funds Added Successfully!')
        return redirect(url_for('add_funds'))

    return render_template('add_funds.html', form=form)

@app.route("/with_funds", methods=["GET", "POST"])
def with_funds():

    form = WithFundsForm()

    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('Funds Withdrawn Successfully!')
        return redirect(url_for('with_funds'))

    return render_template('with_funds.html', form=form)

@app.route("/market", methods=["GET", "POST"])
def market(): 
    form = MarketHours()
    
    if form.validate_on_submit():  #Adjust later to fulfill database needs
        flash('The market hours have been adjusted')
        return redirect(url_for('market'))

    new_hours = MarketHours(start_time = form.start_time.data, end_time = form.end_time.data, start_day = form.start_day.data, end_day = form.end_day.data)

    return render_template('market.html', form=form)

@app.route("/trans_history", methods=["GET", "POST"]) #Adjust later for database
def trans_history():

    return render_template('trans_history.html')