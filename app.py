from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

app.config['SECRET_KEY'] = 'temp_key' #Change key later

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['WTF_CSRF_ENABLED'] = False

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
    return render_template('login.html')