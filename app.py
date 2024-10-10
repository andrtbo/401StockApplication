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

# Classes for database and forms
class UserForm(FlaskForm): #Form with fields required for logging in
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route("/")
def dashboard():
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