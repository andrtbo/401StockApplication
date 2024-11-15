import datetime
from datetime import datetime
import random
from flask import flash
from .models import *

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

def unique_stock(input_stock):
    try:
        test_stock = Stock.query.filter_by(stock_ticker = input_stock.stock_ticker).first()
        if test_stock.stock_ticker == input_stock.stock_ticker:
            flash("This stock ticker is already in use.")
            return False
    except AttributeError:
        try:
            test_stock = Stock.query.filter_by(company_name = input_stock.company_name).first()
            if test_stock.company_name == input_stock.company_name:
                flash("The company name is already in use.")
                return False
        except AttributeError:
            return True

def record_transaction(ticker, volume, price, current_user):
    timestamp = datetime.now().strftime("%m/%d/%Y %I:%M %p")

    new_transaction = Transactions(
        id = current_user.id,
        stock_ticker = ticker,
        purchase_price = price,
        purchase_volume = volume,
        transaction_time = timestamp
    )

    db.session.add(new_transaction)

def time_conv(time):
    if type(time) == type('str'): 
        num_time = int(time[:-6]) # Converts time string to 0-11 value
        if time[-2:] == "PM": # Add 12 if it's PM
            num_time += 12
        if num_time == 12: # Subtract 12 if it's 12 AM or 12 PM
            num_time -= 12
        if time[2:-3] != '00' and time[2:2] == ':': # If it's between hours (Current time), note that
            num_time += .5
        return num_time
    if type(time) == type(1): # Converts 0-23 value to time string
        match time:
            case time if time == 0:
                return('12:00 AM')
            case time if time == 12:
                return('12:00 PM')
            case time if time > 12:
                return(str(time - 12) + ":00 PM")
            case time if time < 12:
                return(str(time) + ":00 AM")
            
def day_conv(day):
    match day: # Uses 0-6 so it matches datetime.datetime.today().weekday()
        case day if day == 'Monday':
            return 0
        case day if day == 'Tuesday':
            return 1
        case day if day == 'Wednesday':
            return 2
        case day if day == 'Thursday':
            return 3
        case day if day == 'Friday':
            return 4
        case day if day == 'Saturday':
            return 5
        case day if day == 'Sunday':
            return 6

def check_hours(current_hours):
    # Convert the datebase's string values into comparable integers
    start_time = time_conv(current_hours.start_time)
    end_time = time_conv(current_hours.end_time)
    start_day = day_conv(current_hours.start_day)
    end_day = day_conv(current_hours.end_day)

    # Get the current time and day with the same integer mappings
    current_time = time_conv(datetime.now().strftime('%I:%M %p')[1:])
    current_day = datetime.today().weekday()

    # Check if the current time is outside of operating hours
    if start_time != end_time and (start_time > current_time or current_time > end_time): 
        return(False)
    elif start_day > end_day and (start_day < current_day < end_day):
        return(False)
    elif start_day < end_day and (start_day > current_day or current_day > end_day):
        return(False)

    return(True)

def update_stock():
    stocks = Stock.query.all()

    last_updated = LastUpdated.query.first()
    last_dt = datetime.strptime(last_updated.time, '%Y-%m-%d %H:%M:%S')
    current_dt = datetime.now()
    delta = current_dt - last_dt

    if delta.total_seconds() > 300:
        for stock in stocks:
            flux = random.uniform(-0.05, 0.05)
            stock.market_price = float("{:.2f}".format(stock.market_price * (1 + flux)))
            last_updated.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            stock_update = StockHistory(
                stock_ticker = stock.stock_ticker,
                price = stock.market_price,
                time = last_updated.time
            )
            db.session.add(stock_update)

            db.session.commit()

def daily_highlow(stock):
    valid_updates = []
    
    try:
        opening_price = stock.opening_price + 0
    except TypeError:
        opening_price = stock.market_price

    stock_history = StockHistory.query.filter_by(stock_ticker = stock.stock_ticker).all()
    for update in stock_history:
        time = datetime.strptime(update.time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        delta = current_time - time
        if delta.total_seconds() > 24*3600:
            opening_price = update.price
            break
        else:
            valid_updates.append(update.price)

    try:
        return opening_price, min(valid_updates), max(valid_updates)
    except ValueError:
        return opening_price, stock.market_price, stock.market_price

def update_daily():
    stocks = Stock.query.all()
    for stock in stocks:
        try:
            stock.opening_price = stock.opening_price + 0
        except TypeError:
            stock.opening_price = stock.market_price

        stock.opening_price, stock.daily_low, stock.daily_high = daily_highlow(stock)
    db.session.commit()

def paginate(transactions, page):
    if len(transactions) < 10:
        page_count = 1
    else:
        page_count = len(transactions) // 10 + 1

    page_transactions = transactions[(page-1)*10:page*10]
    
    return page_count, page_transactions

