from flask import Blueprint, render_template, send_from_directory
import yfinance as yf
import json 
from datetime import date


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
