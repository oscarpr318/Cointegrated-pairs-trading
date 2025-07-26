import yfinance as yf
import pandas as pd
import datetime

def fetch_data():

    glenData = yf.Ticker("GLEN.L")
    camlData = yf.Ticker("CAML.L")

    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.today() - datetime.timedelta(days=10*365)).strftime("%Y-%m-%d")

    glenDataDF = pd.DataFrame(glenData.history(start=start_date,end=end_date))
    camlDataDF = pd.DataFrame(camlData.history(start=start_date,end=end_date))

    return glenDataDF,camlDataDF