from math import log,sqrt
from numpy import mean,std,array

# A is caml B is glen
# For each stock of caml we buy <hedgingRatio> amount of glen
def spread(a,b,hedgingRatio):
    return log(a)-hedgingRatio*log(b)

def calculateSharpeRatio(bankrolls):

    # Convert bankrolls to daily returns
    bankrolls = array(bankrolls)
    daily_returns = bankrolls[1:] / bankrolls[:-1] - 1

    # Risk-free rate: UK 3-month Treasury yield (~5.25% annually)
    risk_free_annual = 5.25
    risk_free_daily  = risk_free_annual / 252  # convert to daily

    # Calculate excess returns
    excess_returns = daily_returns - risk_free_daily

    # Sharpe ratio
    sharpe_ratio = mean(excess_returns) / std(excess_returns)

    # Annualize Sharpe ratio
    sharpe_ratio_annualized = sharpe_ratio * sqrt(252)

    print(f"Daily Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Annualized Sharpe Ratio: {sharpe_ratio_annualized:.2f}")
