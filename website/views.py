from flask import Blueprint, render_template, send_from_directory, request, jsonify, abort
import yfinance as yf
import json 
from datetime import datetime, timedelta
from .models import StockData, db, Holidays
from sqlalchemy import desc, asc, not_

views = Blueprint('views', __name__)

@views.route('/')
def home():
    def get_xu100_data():
        # Get current xu100 value
        xu100 = yf.Ticker('XU100.IS')
        xu100history = xu100.history(period='1d')
        current_xu100 = xu100history['Close'].iloc[-1]
        # Get the highest value of xu100history['Close']
        highest_xu100_value = xu100history['Close'].max()
        
        # Get today's highest xu100 value
        todays_high_xu100 = xu100history['High'].iloc[-1]
        # Find the date of the highest xu100 value
        date_of_highest_xu100 = xu100history[xu100history['Close'] == highest_xu100_value].index[0].strftime('%Y-%m-%d')
        # Get highest xu100 value ever
        
         # Read the all-time high from the JSON file
        with open('db.json', 'r') as file:
            data = json.load(file)
            all_time_high = data['allTimeHigh']
            date_of_all_time_high = data['dateOfAllTimeHigh']
        # If today's high is greater than the all-time high, update the JSON file
        if highest_xu100_value > all_time_high:
            all_time_high = highest_xu100_value
            date_of_all_time_high = date_of_highest_xu100
        return {
            'current_xu100': current_xu100,
            'todays_high_xu100': todays_high_xu100,
            'all_time_high': all_time_high,
            'date_of_all_time_high': date_of_all_time_high
        }
    
    return render_template("base.html",data = get_xu100_data())

@views.route('/dolar-bazinda')
def dolar_bazinda():
    def get_xu100_usd_data():
            # Get current xu100 value
        xu100 = yf.Ticker('XU100.IS')
        xu100history = xu100.history(period='1d')
        current_xu100 = xu100history['Close'].iloc[-1]
        currentUsdTry = yf.Ticker('USDTRY=X').history(period='1d')['Close'].iloc[-1]
        current_xu100_usd = current_xu100 / currentUsdTry

        # Read the all-time high from the JSON file
        with open('db.json', 'r') as file:
            data = json.load(file)
            all_time_high = data['allTimeHighUSD']
            date_of_all_time_high = data['dateOfAllTimeHighUSD']
        return current_xu100_usd, all_time_high, date_of_all_time_high
    return render_template("dolar-bazinda.html", data=get_xu100_usd_data())

@views.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory('static', 'ads.txt')

def to_dict(stock):
    return {c.name: getattr(stock, c.name) for c in stock.__table__.columns}


@views.route('/data-ad6a65b1-544b-415c-ac85-794c2c8f22e3')
def data():
    stocks = StockData.query.all()
    holidays = Holidays.query.all()
    return jsonify({
        'stock': [stock.to_dict() for stock in stocks],
        'holidays': [holiday.to_dict() for holiday in holidays]
    })

@views.route('/stock-increase-rate', methods=['GET'])
def get_stock_increase_rates():
    take = request.args.get('take', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    is_asc = request.args.get('asc')
    sort = request.args.get('sort', default='increase_1d', type=str)


    

    
    query = StockData.query.filter(StockData.date == datetime.now().date().strftime('%Y-%m-%d'))
    query = query.filter(not_(getattr(StockData, sort).is_(None)))

    if is_asc in ['true', '1', 'True']:
        query = query.order_by(asc(sort))
    else:
        query = query.order_by(desc(sort))

    stocks = query.paginate(page=take, per_page = page_size, error_out=False).items

    return jsonify([
            to_dict(stock)
            for stock in stocks
        ])