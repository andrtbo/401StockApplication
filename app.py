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

@app.route("/")
def dashboard():
    db.create_all()
    return render_template('dashboard.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        account = User.query.filter_by(username = form.username.data).first()
        
        if account.password == form.password.data:
            flash('Login successful')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful')

    return render_template('login.html', form=form)

@app.route("/create-account", methods=["GET", "POST"])
def create_account():
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
    return render_template('buy_stock.html')

@app.route("/sell_stock", methods=["GET", "POST"])
def sell_stock():
    return render_template('sell_stock.html')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')