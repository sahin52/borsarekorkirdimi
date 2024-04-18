from flask import Blueprint, render_template, send_from_directory, request, jsonify, abort
import yfinance as yf
import json 
from datetime import datetime, timedelta
from flask import current_app
from website.helper_methods import update_stock_data_in_db
from .models import XU100, StockData, db, Holidays
from sqlalchemy import desc, asc, not_

views = Blueprint('views', __name__)

def get_xu100_data():
    # Get current xu100 value
    latest_res = XU100.query.order_by(XU100.latest_update_date.desc()).first()
    
    return {
        'current_xu100': latest_res.latest_price,
        'todays_high_xu100': latest_res.todays_highest_price,
        'date_of_todays_high': latest_res.latest_price_date,
        'all_time_high': latest_res.last_record,
        'date_of_all_time_high': latest_res.last_record_date,
    }


@views.route('/')
def home():    
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
        # latest_res = XU100.query.filter(XU100.all_time_high_usd is not None).order_by(XU100.latest_update_date.desc()).first()
        #TODO: hard coded date and value
        return current_xu100_usd, 510.37,  "2013-05-17"
    return render_template("dolar-bazinda.html", data=get_xu100_usd_data())

@views.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory('static', 'ads.txt')

@views.route('/robots.txt')
def serve_robots_txt():
    return send_from_directory('static','robots.txt')


def to_dict(stock):
    return {c.name: getattr(stock, c.name) for c in stock.__table__.columns}


@views.route('/data-ad6a65b1-544b-415c-ac85-794c2c8f22e3')
def data():
    is_stock_wanted = request.args.get('stock', default=False, type=bool)
    is_holiday_wanted = request.args.get('holiday', default=False, type=bool)
    stocks = StockData.query.all()
    holidays = Holidays.query.all()
    if( is_stock_wanted):
        stocks = StockData.query.all()
        return jsonify({
            'stock': [to_dict(stock) for stock in stocks]
        })
    if( is_holiday_wanted):
        holidays = Holidays.query.all()
        return jsonify({
            'holidays': [to_dict(holiday) for holiday in holidays]
        })
    

    return jsonify({
        'stock': [to_dict(stock) for stock in stocks],
        'holidays': [to_dict(holiday) for holiday in holidays]
    })

@views.route('/stock-increase-rate', methods=['GET'])
def get_stock_increase_rates():
    take = request.args.get('take', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    is_asc = request.args.get('asc')
    sort = request.args.get('sort', default='increase_1d', type=str)

    if StockData.query.first() is None:
        update_stock_data_in_db(current_app)


    

    
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