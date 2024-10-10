from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy, ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp_key' #Change key later
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['WTF_CSRF_ENABLED'] = False

#Classes for the database
class User(db.model):
    user_id = db.column(db.Integer, primary_key = True)
    username = db.column(db.String(255), unique = True, nullable = False)
    first_name = db.column(db.String(20))
    last_name = db.column(db.String(20))
    email = db.column(db.String(100), unique = True, nullable = False)
    password_hash = db.column(db.String(255))
    privileges = db.column(db.boolean)

class Stock(db.model):
    stock_ticker = db.column(db.String(5), primary_key = True)
    company_name = db.column(db.String(255))
    market_price = db.column(db.Float, nullable = False)
    volume_owned = db.column(db.Integer)
    market_volume = db.column(db.Integer)

class Portfolio(db.model):
    portfolio_id = db.column(db.Integer, primary_key = True)
    user_id = db.column(db.Integer, db.ForeignKey(User.user_id))
    stock_ticker = db.column(db.Integer, db.ForeignKey(Stock.stock_ticker))
    total_balance = db.column(db.Float)
    cash_balance = db.column(db.Float)  

class Transactions(db.model):
    transaction_id = db.column(db.Integer, primary_key = True)
    user_id = db.column(db.Integer, db.ForeignKey(User.user_id))
    stock_ticker = db.column(db.Integer, db.ForeignKey(Stock.stock_ticker))
    purchase_price = db.column(db.Float)
    purchase_volume = db.column(db.Integer)

# Classes for database and forms
class UserForm(FlaskForm): #Form with fields required for logging in
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def dashboard():
    db.create_all()
    return render_template('dashboard.html')

@app.route("/buy_stock") 
def buy_stock():
    return render_template('buy_stock.html')

@app.route("/sell_stock")
def sell_stock():
    return render_template('sell_stock.html')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

@app.route("/login")
def login():
    form = UserForm()

    return render_template('login.html', form=form)

@app.route("/create-account")
def create_account():
    form = UserForm()
    
    return render_template('create_account.html', form=form)