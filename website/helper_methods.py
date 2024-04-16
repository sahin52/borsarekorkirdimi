from datetime import timedelta
from .models import StockData, db, Holidays
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse


def get_historical_stock_data():
    # Get the stock data from the database
    stock_data = StockData.query.all()
    return stock_data





def is_holiday(date):
    """
    Check if the given date is a holiday.
    ##### please use string format "yyyy-MM-dd"
    """

    if(parse(date).weekday() >= 5):
        return True
    
    does_date_exist = Holidays.does_date_exist(date)
    if(does_date_exist):
        return Holidays.is_holiday(date)
    does_xu100_data_exist = check_is_holiday_from_xu100(date)
    if(does_xu100_data_exist):
        Holidays.add(Holidays(date=date, is_holiday=True))
        return True
    return False

def check_is_holiday_from_xu100(date):
    """
    uses yfinance to check if xu100 data exists for the date
    date must be in "yyyy-MM-dd" format
    """
    # Check if today is a holiday
    date_parsed = parse(date)
    one_day_later = date_parsed + timedelta(days=1)
    data = yf.download('XU100.IS', start=date, end=one_day_later)
    return data.empty # If the data is empty, it means that the date is a holiday
