import yfinance as yf
import json
import sqlite3
from datetime import datetime

# stocks = [
# 'A1CAP.IS',
# 'ACSEL.IS',
# 'ADEL.IS',
# 'ADESE.IS',
# 'ADGYO.IS',
# 'AEFES.IS']

# import concurrent.futures

# Connect to the SQLite database
conn = sqlite3.connect('stock_data2.sqlite3')

# Create the StockData table if it doesn't exist
conn.execute('''
    CREATE TABLE IF NOT EXISTS StockData (
        data_id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT,
        date DATE,
        interval TEXT,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume INTEGER,
        UNIQUE(stock_name, date, interval)
    )
''')


import json

# Open the file and load the data
with open('data.json', 'r') as f:
    combined_data = json.load(f)

# def get_ticker_data(stock):
#     tickerData = yf.Ticker(stock+'.IS')
#     tickerDf = tickerData.history(period='1d', start='2023-7-4', end='2024-7-4')
#     return stock, tickerDf.to_dict()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     results = executor.map(get_ticker_data, stocks)

# combined_data = {}
# for stock, data in results:
#     combined_data[stock] = data

# Convert timestamps to strings
data_for_json = {}
for stock in combined_data:
    data_for_json[stock] = {}
    for key in combined_data[stock]:
        if (key not in ['Dividends', 'Stock Splits','Volume']):
            data_for_json[stock][key] = {str(date): value for date, value in combined_data[stock][key].items()}

# # Write the combined data to a JSON file
# with open('data.json', 'r') as file:
#     existing_data = json.load(file)
#     existing_data.update(data_for_json)

# with open('data.json', 'w') as file:
#     json.dump(existing_data, file)

# Insert the data into the StockData table
interval = '1d'
for stock, data in data_for_json.items():
    # Get all dates for this stock
    dates = data['Open'].keys()

    for date in dates:
        open_value = data['Open'][date]
        high_value = data['High'][date]
        low_value = data['Low'][date]
        close_value = data['Close'][date]
        date2 = datetime.fromisoformat(date).isoformat()
        # volume_value = data['Volume'][date]

        conn.execute('''
            INSERT INTO StockData (stock_name, date, interval, open, high, low, close)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (stock, date2,interval, open_value, high_value, low_value, close_value))
# Commit the changes and close the connection
conn.commit()
conn.close()