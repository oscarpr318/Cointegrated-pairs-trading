from data_loader import fetch_data
from pairs_trading import regress_data, backtest_strategy

if __name__ == "__main__":

    glenDataDF,camlDataDF = fetch_data()


    noOfElements = len(glenDataDF["Close"])
    glenTraingDataDF = glenDataDF.iloc[:-1*int(0.4*noOfElements)]
    noOfElements = len(camlDataDF["Close"])
    camlTraingDataDF = camlDataDF.iloc[:-1*int(0.4*noOfElements)]


    hedgingRatio = regress_data(camlTraingDataDF,glenTraingDataDF)

    noOfElements = len(glenDataDF["Close"])
    glenTestingDataDF = glenDataDF.iloc[int(0.6*noOfElements):]
    noOfElements = len(camlDataDF["Close"])
    camlTestingDataDF = camlDataDF.iloc[int(0.6*noOfElements):]
    

    backtest_strategy(camlTestingDataDF,glenTestingDataDF,hedgingRatio) 