from .extensions import db

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
    start_day = db.Column(db.String(10))
    end_day = db.Column(db.String(10))