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

# Variables for logging in
logged_in = False # Used to check if user is logged in. Change to "True" to access pages without logging in
current_user = User() # User class to temporarily store user information

@app.route("/")
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

    if form.validate_on_submit():
        account = User.query.filter_by(username = form.username.data).first()
        
        if account.password == form.password.data:
            flash('Login successful')
            
            # Sets the user as logged in and modifies the "current_user" object
            logged_in = True
            current_user = User(username = account.username, first_name = account.first_name, last_name = account.last_name, email = account.email, password = account.password, admin = account.admin)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful')

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    global logged_in
    global current_user
    logged_in = False
    current_user = User()
    return redirect(url_for('login'))

@app.route("/create-account", methods=["GET", "POST"])
def create_account():
    global logged_in
    form = CreateForm()
    
    if form.validate_on_submit():
        new_user = User(username = form.username.data, first_name = form.first_name.data, last_name = form.last_name.data, email = form.email.data, password = form.password.data, admin = False)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    
    return render_template('create_account.html', form=form)

@app.route("/buy_stock", methods=["GET", "POST"]) 
def buy_stock():
    global logged_in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        return render_template('buy_stock.html')

@app.route("/sell_stock", methods=["GET", "POST"])
def sell_stock():
    global logged_in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        return render_template('sell_stock.html')

@app.route("/portfolio")
def portfolio():
    global logged_in
    if not logged_in:
        flash('Please log in before accessing stock trading services.')
        return redirect(url_for('login'))
    else:
        return render_template('portfolio.html')