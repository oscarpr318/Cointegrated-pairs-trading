import pandas as pd
from math import sqrt, log
import matplotlib.pyplot as plt
import statsmodels.tsa.stattools as ts
from sklearn.linear_model import LinearRegression
from scipy.stats.stats import pearsonr
from utils import spread, calculateSharpeRatio

def regress_data(camlDataDF,glenDataDF):

    glenDataDF = pd.DataFrame({'GLEN':glenDataDF["Close"].values})
    camlDataDF = pd.DataFrame({'CAML':camlDataDF["Close"].values})

    data = pd.concat([glenDataDF, camlDataDF], axis=1)
    data.dropna(axis=0, how='any',inplace=True)
    independentStock = 'CAML'
    dependentStock = 'GLEN'

    regressionModel = LinearRegression()
    regressionModel.fit(data[independentStock].values.reshape(-1,1),data[dependentStock].values)
    print('parameters: %.7f, %.7f' %(regressionModel.intercept_, regressionModel.coef_))

    yfit = regressionModel.coef_ * data[independentStock] + regressionModel.intercept_
    y_residual = data[dependentStock] - yfit

    fig, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].set_title(independentStock +' vs ' +dependentStock)
    ax[0].plot(data)
    ax[1].set_title('Regression Residual')
    ax[1].plot(y_residual)

    print(ts.adfuller(y_residual, 1) )

    hedgingRatio = pearsonr(data[independentStock], data[dependentStock])[0]
    print(hedgingRatio)

    plt.show()
    
    return hedgingRatio

def check_positions(positions, hedgingRatio, zScore,prev_zScore, camlTestingDataDF,glenTestingDataDF, x):

    daily_pnl = 0

    for p in positions:

        if p["open"] == True:
            
            if p["type"] == "short":

                pnl_glencore = p["caml_no_of_shares"] * hedgingRatio * (p["buy_price"] - glenTestingDataDF["Close"].iloc[x])
                pnl_caml = p["caml_no_of_shares"] * (camlTestingDataDF["Close"].iloc[x] - p["sell_price"])

                daily_pnl += pnl_glencore + pnl_caml

                if prev_zScore > 0 and zScore <= 0:

                    p["open"] = False

                if zScore >= 2.5 and zScore < 3:

                    p["stop_loss"] = True

                if zScore >= 3 and p["stop_loss"] == True:

                    p["open"] = False


            if p["type"] == "long":

                pnl_glencore = p["caml_no_of_shares"] * hedgingRatio * (glenTestingDataDF["Close"].iloc[x] - p["sell_price"])
                pnl_caml = p["caml_no_of_shares"] * (p["buy_price"] - camlTestingDataDF["Close"].iloc[x])

                daily_pnl += pnl_glencore + pnl_caml

                if zScore >= 0 and prev_zScore < 0:

                    p["open"] = False
    
                if zScore <= -2.5 and zScore > -3:

                    p["stop_loss"] = True

                if zScore <= -3 and p["stop_loss"] == True:

                    p["open"] = False


    return daily_pnl

def backtest_strategy(camlTestingDataDF,glenTestingDataDF, hedgingRatio):

    glenTestingDataDF.reset_index(inplace = True)
    camlTestingDataDF.reset_index(inplace = True)

    bankroll = 10000
    prev_zScore = 0
    positions = []
    bankrolls = []
    dates = []

    for x in range(20, min(len(camlTestingDataDF),len(glenTestingDataDF))):

        sumOfSpreads = sum([spread(camlTestingDataDF["Close"].iloc[y], glenTestingDataDF["Close"].iloc[y],hedgingRatio) for y in range(x-20,x)])
        meanSpread = sumOfSpreads/20
        sdSpread = sqrt(sum([(meanSpread-spread(camlTestingDataDF["Close"].iloc[y], glenTestingDataDF["Close"].iloc[y],hedgingRatio))**2 for y in range(x-20,x)]) / 20)
        currentSpread = spread(camlTestingDataDF["Close"].iloc[x], glenTestingDataDF["Close"].iloc[x],hedgingRatio)

        zScore = (currentSpread - meanSpread)/sdSpread

        daily_pnl = check_positions(positions,hedgingRatio, zScore,prev_zScore,camlTestingDataDF,glenTestingDataDF,x)
        bankroll += daily_pnl

        if bankroll > 0:

            if zScore >= 2:
                # short
                # sell A buy B

                stake = bankroll * 0.01
                caml_no_of_shares = stake/camlTestingDataDF["Close"].iloc[x]

                new_position = {"date":glenTestingDataDF['Date'].iloc[x],"type":"short","caml_no_of_shares":caml_no_of_shares, "buy_price":glenTestingDataDF["Close"].iloc[x],"sell_price":camlTestingDataDF["Close"].iloc[x],"open":True,"stop_loss":False}

                positions.append(new_position)

            if zScore <= -2:
                # long
                # buy A sell B
                
                stake = bankroll * 0.01
                caml_no_of_shares = stake/camlTestingDataDF["Close"].iloc[x]

                new_position = {"date":glenTestingDataDF['Date'].iloc[x],"type":"long", "caml_no_of_shares":caml_no_of_shares, "buy_price":camlTestingDataDF["Close"].iloc[x], "sell_price":glenTestingDataDF["Close"].iloc[x],"open":True,"stop_loss":False}

                positions.append(new_position)


        prev_zScore = zScore
        bankrolls.append(bankroll)
        dates.append(glenTestingDataDF["Date"].iloc[x])


    calculateSharpeRatio(bankrolls)

    plt.plot(dates,bankrolls)
    plt.show()

