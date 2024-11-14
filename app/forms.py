from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, SelectField
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
    market_volume = IntegerField('Market Volume', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class AddFundsForm(FlaskForm): #Form to add funds to account
    deposit_amount = FloatField('Deposit Amount', validators=[DataRequired()])
    submit = SubmitField('Add Funds')

class WithFundsForm(FlaskForm): #Form to withdrawal funds from account
    withdraw_amount = FloatField('Withdraw Amount', validators=[DataRequired()])
    submit = SubmitField('Withdraw Funds')

class MarketForm(FlaskForm): #Form to set market hours for application
    start_time = SelectField(choices=[('12', '12:00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'), ('7', '7:00'), ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00')])
    XM_1 = SelectField(choices=[('AM', 'AM'), ('PM', 'PM')])
    end_time = SelectField(choices=[('12', '12:00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'), ('7', '7:00'), ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00')])
    XM_1 = SelectField(choices=[('AM', 'AM'), ('PM', 'PM')])
    XM_2 = SelectField(choices=[('AM', 'AM'), ('PM', 'PM')])
    start_day = SelectField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')])
    end_day = SelectField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')])
    submit = SubmitField()

class TransactionForm(FlaskForm): # Takes input for the volume of stock to be bought/sold
    stock_amount = IntegerField('Volume', validators=[DataRequired()])
    submit = SubmitField()