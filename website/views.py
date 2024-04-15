from flask import Blueprint, render_template, send_from_directory, request, jsonify
import yfinance as yf
import json 
from datetime import datetime, timedelta
from .models import StockData, db
from sqlalchemy import func, desc

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
            with open('db.json', 'w') as file:
                json.dump({'allTimeHigh': all_time_high, 'dateOfAllTimeHigh': date_of_all_time_high}, file)
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

@views.route('/stocks', methods=['GET'])
def get_stocks():
    take = request.args.get('take', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    asc = request.args.get('asc', default=True, type=bool)
    range = request.args.get('range', default='1d', type=str)

    if range == '1d':
        start_date = datetime.now() - timedelta(days=1)
    elif range == '1w':
        start_date = datetime.now() - timedelta(weeks=1)
    elif range == '1m':
        start_date = datetime.now() - timedelta(days=30)
    elif range == '3m':
        start_date = datetime.now() - timedelta(days=90)
    elif range == '6m':
        start_date = datetime.now() - timedelta(days=180)
    elif range == '12m':
        start_date = datetime.now() - timedelta(days=365)

    # For testing
    start_date = datetime.now() - timedelta(days=30)
    query = StockData.query.filter(StockData.date >= start_date)

    if asc:
        query = query.order_by(StockData.date.asc())
    else:
        query = query.order_by(StockData.date.desc())


    # ...

    stocks = (
        db.session.query(
            StockData.stock_name,
            (((func.max(StockData.close) - func.min(StockData.close)) / func.min(StockData.close)) * 100)
            .label("percentage_difference"),
            func.max(StockData.close).label("latest_close"),
            func.min(StockData.close).label("first_close"),
        )
        .filter(StockData.date >= start_date)
        .group_by(StockData.stock_name)
        .order_by("percentage_difference" if asc else desc("percentage_difference"))
        .paginate(page=take, per_page=page_size, error_out=False)
        .items
    )

    return jsonify(
        {
            "stocks": [
                {
                    "stock_name": stock.stock_name,
                    "percentage_difference": stock.percentage_difference,
                    "latest_close": stock.latest_close,
                    "first_close": stock.first_close,
                }
                for stock in stocks
            ]
        }
    )
# Old Code
    stocks = query.paginate(page=take, per_page = page_size, error_out=False).items

    return jsonify({
        'stocks': [
            {
                'date': stock.date.isoformat(),
                'close': stock.close
            }
            for stock in stocks
        ]
    })
