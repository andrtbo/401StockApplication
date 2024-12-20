from .extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(255))
    balance = db.Column(db.Float)
    admin = db.Column(db.Boolean)

class Stock(db.Model):
    stock_ticker = db.Column(db.String(5), primary_key=True)
    opening_price = db.Column(db.Float)
    daily_low = db.Column(db.Float)
    daily_high = db.Column(db.Float)
    company_name = db.Column(db.String(255))
    market_price = db.Column(db.Float, nullable = False)
    market_volume = db.Column(db.Integer)

class OwnedStock(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey(User.id))
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    volume_owned = db.Column(db.Integer)

class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey(User.id))
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    total_balance = db.Column(db.Float)
    cash_balance = db.Column(db.Float)  

class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey(User.id))
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    purchase_price = db.Column(db.Float)
    purchase_volume = db.Column(db.Integer)
    transaction_time = db.Column(db.String(30))

class MarketHours(db.Model):
    start_time = db.Column(db.String(10), primary_key=True)
    end_time = db.Column(db.String(10))
    start_day = db.Column(db.String(10))
    end_day = db.Column(db.String(10))

class LastUpdated(db.Model):
    time = db.Column(db.String(50), primary_key=True)

class StockHistory(db.Model):
    update_id = db.Column(db.Integer, primary_key=True)
    stock_ticker = db.Column(db.String(5), db.ForeignKey(Stock.stock_ticker))
    price = db.Column(db.Float)
    time = db.Column(db.String(50))