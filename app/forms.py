from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email

from .extensions import db

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