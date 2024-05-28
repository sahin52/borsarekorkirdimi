from datetime import timedelta
from .models import StockData, Holidays, XU100, db, UpdateToDb
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse
import calendar
import os
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor
import pytz

def yfdownload(stocks, start, end):
    print("LOG: Downloading data for", stocks[:5], "from", start, "to", end, "stack trace:")
    stack = traceback.extract_stack(limit=5)
    for frame in stack[:-1]:
        print(f'File: {frame.filename}, line: {frame.lineno}, function: {frame.name}')
    return yf.download(stocks, start=start, end=end, progress=False)

def data_exists_in_db():
    """
    Check if the Firestore database has any data
    """
    docs = db.collection('StockData').limit(1).stream()
    return any(docs)

lock = threading.Lock()

def fetch_and_store_data(app, date, stocks):
    with app.app_context():
        data = yfdownload(stocks, start=date, end=(parse(date) + timedelta(days=1)).strftime("%Y-%m-%d"))
        stock_datas = []
        for stock in stocks:
            stock_data = StockData(stock_name=stock)
            stock_data.date = date
            stock_data.close = data['Close'][stock].iloc[-1]
            stock_datas.append(stock_data)
        StockData.add_all(stock_datas)

def update_stock_data_in_db(app):

    # We need to check if the database needs an update, because this method is called by different sources
    # if today is holiday, we will not update the database 
    # but if the request is coming from the user, we have to update the datase
    with lock:
        with app.app_context():
            try:
                if (data_exists_in_db() and not is_working_hour(datetime.now().hour, datetime.now().minute)):
                    return # if there is data and it is not working hour, let it go
                if((UpdateToDb.get_latest_update() is not None) and UpdateToDb.get_latest_update()['last_update'] > (datetime.now(pytz.UTC) - timedelta(minutes=15))):
                    return # return if the latest update is within 15 minutes - only update every 15 minutes
                update_xu100_in_db()

                # either there is no data, or it needs an update

                # last_working_day = datetime.now().strftime("%Y-%m-%d") # initially today
                # if((datetime.now().hour < 10 or (datetime.now().hour == 10 and datetime.now().minute < 16))): # if morning hours, we will get the data of yesterday
                #     last_working_day = get_last_work_day((parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d"))

                # one_day_earlier = get_last_work_day((parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d"))
                # today = datetime.now().strftime("%Y-%m-%d")
                # # for other dates, we will return the difference for specific days
                # one_week_earlier = get_last_work_day((parse(today) - timedelta(days=7)).strftime("%Y-%m-%d"))
                # one_month_earlier = get_last_work_day((parse(today) - timedelta(days=30)).strftime("%Y-%m-%d"))
                # six_months_earlier = get_last_work_day((parse(today) - timedelta(days=183)).strftime("%Y-%m-%d"))
                # one_year_earlier = get_last_work_day((parse(today) - timedelta(days=365)).strftime("%Y-%m-%d"))
                # five_years_earlier = get_last_work_day((parse(today) - timedelta(days=1826)).strftime("%Y-%m-%d"))
                # stocks = ['AEFES.IS',
                # 'AGROT.IS',
                # 'AHGAZ.IS',
                # 'AKBNK.IS',
                # 'AKCNS.IS',
                # 'AKFGY.IS',
                # 'AKFYE.IS',
                # 'AKSA.IS',
                # 'AKSEN.IS',
                # 'ALARK.IS',
                # 'ALBRK.IS',
                # 'ALFAS.IS',
                # 'ANSGR.IS',
                # 'ARCLK.IS',
                # 'ASELS.IS',
                # 'ASTOR.IS',
                # 'BERA.IS',
                # 'BFREN.IS',
                # 'BIENY.IS',
                # 'BIMAS.IS',
                # 'BIOEN.IS',
                # 'BOBET.IS',
                # 'BRSAN.IS',
                # 'BRYAT.IS',
                # 'BTCIM.IS',
                # 'CANTE.IS',
                # 'CCOLA.IS',
                # 'CIMSA.IS',
                # 'CWENE.IS',
                # 'DOAS.IS',
                # 'DOHOL.IS',
                # 'ECILC.IS',
                # 'ECZYT.IS',
                # 'EGEEN.IS',
                # 'EKGYO.IS',
                # 'ENERY.IS',
                # 'ENJSA.IS',
                # 'ENKAI.IS',
                # 'EREGL.IS',
                # 'EUPWR.IS',
                # 'EUREN.IS',
                # 'FROTO.IS',
                # 'GARAN.IS',
                # 'GESAN.IS',
                # 'GUBRF.IS',
                # 'GWIND.IS',
                # 'HALKB.IS',
                # 'HEKTS.IS',
                # 'IPEKE.IS',
                # 'ISCTR.IS',
                # 'ISGYO.IS',
                # 'ISMEN.IS',
                # 'IZENR.IS',
                # 'KAYSE.IS',
                # 'KCAER.IS',
                # 'KCHOL.IS',
                # 'KLSER.IS',
                # 'KONTR.IS',
                # 'KONYA.IS',
                # 'KOZAA.IS',
                # 'KOZAL.IS',
                # 'KRDMD.IS',
                # 'MAVI.IS',
                # 'MGROS.IS',
                # 'MIATK.IS',
                # 'ODAS.IS',
                # 'OTKAR.IS',
                # 'OYAKC.IS',
                # 'PETKM.IS',
                # 'PGSUS.IS',
                # 'QUAGR.IS',
                # 'REEDR.IS',
                # 'SAHOL.IS',
                # 'SASA.IS',
                # 'SAYAS.IS',
                # 'SDTTR.IS',
                # 'SISE.IS',
                # 'SKBNK.IS',
                # 'SMRTG.IS',
                # 'SOKM.IS',
                # 'TABGD.IS',
                # 'TAVHL.IS',
                # 'TCELL.IS',
                # 'THYAO.IS',
                # 'TKFEN.IS',
                # 'TOASO.IS',
                # 'TSKB.IS',
                # 'TTKOM.IS',
                # 'TTRAK.IS',
                # 'TUKAS.IS',
                # 'TUPRS.IS',
                # 'TURSG.IS',
                # 'ULKER.IS',
                # 'VAKBN.IS',
                # 'VESBE.IS',
                # 'VESTL.IS',
                # 'YEOTK.IS',
                # 'YKBNK.IS',
                # 'YYLGD.IS',
                # 'ZOREN.IS']
                # if(os.getenv('DEV_ENVIRONMENT')):
                #     stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','XU100.IS']
                # data_from_db_for_one_day_earlier = StockData.query.filter(StockData.date == one_day_earlier).all()
                # data_from_db_for_one_week_earlier = StockData.query.filter(StockData.date == one_week_earlier).all()
                # data_from_db_for_one_month_earlier = StockData.query.filter(StockData.date == one_month_earlier).all()
                # data_from_db_for_six_months_earlier = StockData.query.filter(StockData.date == six_months_earlier).all()
                # data_from_db_for_one_year_earlier = StockData.query.filter(StockData.date == one_year_earlier).all()
                # data_from_db_for_five_years_earlier = StockData.query.filter(StockData.date == five_years_earlier).all()

                
                
                # if(len(data_from_db_for_one_day_earlier)==0):
                #     fetch_and_store_data(app, one_day_earlier, stocks)
                # if(len(data_from_db_for_one_week_earlier)==0):
                #     fetch_and_store_data(app, one_week_earlier, stocks)
                # if len(data_from_db_for_one_month_earlier) == 0:
                #     fetch_and_store_data(app, one_month_earlier, stocks)
                # if len(data_from_db_for_six_months_earlier) == 0:
                #     fetch_and_store_data(app, six_months_earlier, stocks)
                # if len(data_from_db_for_one_year_earlier) == 0:
                #     fetch_and_store_data(app, one_year_earlier, stocks)
                # if len(data_from_db_for_five_years_earlier) == 0:
                #     fetch_and_store_data(app, five_years_earlier, stocks)

                # data_from_db_for_last_working_day = StockData.query.filter(StockData.date == last_working_day).all() 
                # data_from_db_for_one_day_earlier = StockData.query.filter(StockData.date == one_day_earlier).all()
                # data_from_db_for_one_week_earlier = StockData.query.filter(StockData.date == one_week_earlier).all()
                # data_from_db_for_one_month_earlier = StockData.query.filter(StockData.date == one_month_earlier).all()
                # data_from_db_for_six_months_earlier = StockData.query.filter(StockData.date == six_months_earlier).all()
                # data_from_db_for_one_year_earlier = StockData.query.filter(StockData.date == one_year_earlier).all()
                # data_from_db_for_five_years_earlier = StockData.query.filter(StockData.date == five_years_earlier).all()

                # latest_data_from_yfinance = yfdownload(stocks, start=last_working_day, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
                
                # stock_datas = []
                # # save latest data to db
                # for stock in stocks:
                #     if(stock in map(lambda it: it.stock_name, data_from_db_for_last_working_day)):
                #         stock_data = next((item for item in data_from_db_for_last_working_day if item.stock_name == stock), None)

                #     else:    
                #         stock_data = StockData(stock_name=stock)
                #         stock_data.date = today
                #         stock_data.interval = "1d"
                #     stock_data.close = latest_data_from_yfinance['Close'][stock].iloc[-1]
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_one_day_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_1d = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_one_day_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_1w = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_one_month_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_1m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_six_months_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_6m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_one_year_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_1y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                    
                #     filtered_data = list(filter(lambda x: x.stock_name==stock, data_from_db_for_five_years_earlier))
                #     if filtered_data and filtered_data[0] and filtered_data[0].close:
                #         stock_data.increase_5y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - filtered_data[0].close) / filtered_data[0].close
                #     stock_datas.append(stock_data)
                # StockData.add_all(stock_datas)
                
                
                UpdateToDb.set_latest_update()
            except Exception as e:
                print("ERROR_OCCURED:", e)
                traceback.print_exc()
                return

def update_xu100_in_db():
    #region XU100 RECORD
    one_week_earlier = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    # get the data of XU100
    all_data = yfdownload(['XU100.IS'], start=one_week_earlier, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
    xu100_data = all_data['Close']
    # get date of the latest price
    latest_price_date = xu100_data.index[-1].strftime("%Y-%m-%d")
    # get latest price
    latest_price = xu100_data.iloc[-1]
    # get the highest price ever in the data
    # but firstly we will filter to only last year
    high_prices = all_data['High']
    last_year_data = high_prices[high_prices.index >= (datetime.now() - timedelta(days=500))]
    highest_price = last_year_data.max()
    # get the date of the highest price
    highest_price_date = last_year_data.idxmax().strftime("%Y-%m-%d")
    
    # get todays highest price
    todays_highest_price = all_data['High'].iloc[-1]
    # add the data to db

    # all_time_high_usd = 510.37 # HARD CODED, since it is so hard for this record to get broken, may update in 3 years
    # date_of_all_time_high_usd = "2013-05-17"
    xu100_data = {
        'latest_update_date': '2022-01-01T00:00:00Z',
        'latest_price': 123.45,
        'latest_price_date': '2022-01-01',
        'last_record': 123.45,
        'last_record_date': '2022-01-01',
        'todays_highest_price': 123.45,
    }
    XU100.add(xu100_data)

#endregion

def is_working_hour(hour, minute):
    """
    Check if the given hour is between 9:45 and 18:30
    """

    if hour < 9 or hour > 18:
        return False
    if hour == 9 and minute < 45:
        return False
    if hour == 18 and minute > 30:
        return False
    return True

def get_next_work_day(date):
    """
    Get the next work day after the given date
    date must be in "yyyy-MM-dd" format
    returns date as string in "yyyy-MM-dd" format
    returns the given date if it is not a holiday
    TODO: create a better way, this is not efficient
    """
    if parse(date) > datetime.now():
        return None
    
    while check_is_holiday(date):
        date = (parse(date) + timedelta(days=1)).strftime("%Y-%m-%d")
    return date

def get_last_work_day(date):
    """
    Get the last work day before the given date
    date must be in "yyyy-MM-dd" format
    returns date as string in "yyyy-MM-dd" format
    returns the given date if it is not a holiday

    """

    while check_is_holiday(date):
        date = (parse(date) - timedelta(days=1)).strftime("%Y-%m-%d")
    return date


def check_is_holiday(date):
    """
    Check if the given date is a holiday.
    ##### please use string format "yyyy-MM-dd"
    returns false for later dates
    """

    if(parse(date).weekday() >= 5):
        return True
    if(parse(date) > datetime.now()): # the date has not come yet, you should not be checking if a later date is a holiday because we are not sure
        raise ValueError("ERROR: The given date is later than today.")
 
    
    does_date_exist = Holidays.does_date_exist(date)
    if(does_date_exist):
        return Holidays.check_is_holiday(date)
    is_holiday_from_xu100 = check_is_holiday_from_xu100(date)
    if(is_holiday_from_xu100): # it is not a holiday, xu100 data exist
        Holidays.add(Holidays(date=date, is_holiday=True))
        return True
    Holidays.add(Holidays(date=date, is_holiday=False))
    return False

def check_is_holiday_from_xu100(date):
    """
    uses yfinance to check if xu100 data exists for the date
    date must be in "yyyy-MM-dd" format
    checks the local db also first
    ##### returns true if the date is holiday
    """
    # Check if today is a holiday
    date_parsed = parse(date)
    one_day_later = date_parsed + timedelta(days=1)
    xu100_from_db = StockData.query.filter(StockData.stock_name == "XU100.IS" and StockData.date == date)
    if xu100_from_db.first() is not None:
        return False
    data = yfdownload('XU100.IS', start=date, end=one_day_later)
    is_holiday = data.empty
    return is_holiday # If the data is empty, it means that the date is a holiday

def get_days_in_last_month():
    """
    returns how many days does the last month have
    """
    current_date = datetime.now()
    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    last_month = last_day_of_previous_month.month
    year_of_last_month = last_day_of_previous_month.year
    days_in_last_month = calendar.monthrange(year_of_last_month, last_month)[1]
    return days_in_last_month

# region Tests

def test_check_is_holiday():
    dates_and_expected_results = [
        ("2024-04-10", True),
        ("2024-04-11", True),
        ("2024-04-12", True),
        ("2024-04-13", True),
        ("2024-04-14", True),
        ("2024-04-15", False),
        ("2024-04-16", False),
        ("2024-04-17", False),
        ("2024-04-09", False),
        ("2024-04-08", False),
        ("2024-04-07", True)
       ]
    for date, expected_result in dates_and_expected_results:
        assert check_is_holiday(date) == expected_result

#endregion