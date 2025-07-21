# Cointegrated pairs trading

1. Introduction

This repository implements a statistical arbitrage trading strategy based on cointegrated pairs trading. The underlying idea is to identify two stocks whose prices move together over time due to an underlying economic or market relationship. When the price spread between the two temporarily diverges from its historical mean, the strategy enters a long/short trade to profit from the expected reversion.

The strategy uses historical price data of Glencore PLC (GLEN.L) and Central Asia Metals PLC (CAML.L). It calculates a hedging ratio via linear regression, tests for cointegration, constructs a mean-reverting spread, and then uses z-score thresholds to determine entry and exit points. A backtesting framework simulates trading performance, including P&L tracking and stop-loss management.
2. Data Pipeline (data_loader.py)

Data is sourced from Yahoo Finance using the yfinance library.

    Assets:

        GLEN.L – Glencore PLC

        CAML.L – Central Asia Metals PLC

    Historical Window:

        10 years of daily data (from today minus 10 years to today).

    DataFrames:

        Each asset’s historical data is loaded into a Pandas DataFrame with standard OHLCV fields.

        Only the Close prices are used for regression, spread calculation, and backtesting.

The function fetch_data() returns:

glenDataDF, camlDataDF

These are the basis for both training (model calibration) and testing (backtesting) datasets.
3. Regression & Hedge Ratio Calculation (pairs_trading.py)

The function regress_data(camlDataDF, glenDataDF) performs:

    Linear Regression:

        Independent variable: CAML’s closing price

        Dependent variable: GLEN’s closing price

        Fits:
        GLEN=β⋅CAML+α
        GLEN=β⋅CAML+α

        Returns the fitted line, residuals, and prints regression parameters.

    Cointegration Test:

        Runs the Augmented Dickey-Fuller (ADF) test on regression residuals to determine if the spread is stationary.

        Stationary residuals imply the two series are cointegrated, supporting a mean-reversion strategy.

    Hedging Ratio:

        Instead of using ββ, the code computes the Pearson correlation coefficient between CAML and GLEN as hedgingRatio.

        This hedgingRatio scales GLEN’s exposure relative to CAML to construct a neutral spread.

    Visualization:

        Plots the historical price relationship and regression residuals.

4. Trading Logic & Position Management
4.1 Spread Calculation (utils.py)

The spread between CAML and GLEN is defined as:
spread=ln⁡(CAML)−hedgingRatio⋅ln⁡(GLEN)
spread=ln(CAML)−hedgingRatio⋅ln(GLEN)

This normalizes prices (log transformation) and adjusts for the hedge ratio.
4.2 Z-Score and Entry Conditions

    A 20-day rolling window is used to compute:

        Mean spread (μμ)

        Standard deviation (σσ)

    Current z-score:

z=spreadt−μσ
z=σspreadt​−μ​

    Entry signals:

        z ≥ +2: Spread is wider than expected → short CAML, long GLEN

        z ≤ -2: Spread is narrower than expected → long CAML, short GLEN

4.3 Position Sizing

    Uses 1% of current bankroll per trade.

    Number of CAML shares:

caml_no_of_shares=stakeCAML close price
caml_no_of_shares=CAML close pricestake​
4.4 Exit Conditions & Stop-Loss Management

    Positions are closed when the spread mean-reverts:

        Short positions: Exit when z-score crosses below 0.

        Long positions: Exit when z-score crosses above 0.

    Stop-loss:

        Activated if z-score moves further against the position beyond ±2.5.

        Forced exit at ±3 standard deviations if the move continues.

4.5 Daily P&L Calculation (check_positions)

    Computes the profit and loss for all open positions based on price changes in CAML and GLEN.

    P&L per position:

        Short trade:
        PnL=ΔGLEN⋅hedgingRatio⋅shares+ΔCAML⋅shares
        PnL=ΔGLEN⋅hedgingRatio⋅shares+ΔCAML⋅shares

        Long trade:
        PnL=ΔGLEN⋅hedgingRatio⋅shares+ΔCAML⋅shares
        PnL=ΔGLEN⋅hedgingRatio⋅shares+ΔCAML⋅shares

    Updates bankroll each day.

5. Backtesting Engine (backtest_strategy)

The backtester simulates the strategy’s performance on unseen historical data:

    Portfolio Initialization:

        Starting bankroll: 10,000 units.

        Tracks:

            Open positions (positions)

            Historical bankroll values (bankrolls)

            Trade dates (dates)

            Monthly returns (monthly_returns)

    Trading Loop:

        Iterates over testing period with a 20-day warm-up window.

        Calculates rolling mean and standard deviation of spread.

        Computes daily z-score and triggers trades based on thresholds.

        Evaluates all open positions, updates bankroll with daily P&L.

        Records bankroll trajectory for later visualization.

    Monthly Performance Tracking:

        At every ~30 trading days, computes:
        monthly return (%)=bankrollprevious month bankroll−1
        monthly return (%)=previous month bankrollbankroll​−1

    Result Visualization:

        Plots bankroll vs. time to show the equity curve.

6. Key Assumptions & Limitations

    Pair Selection: Only CAML and GLEN are tested; no automated pair selection.

    Hedging Ratio: Uses correlation coefficient, not regression slope, which may under/over-hedge.

    Stationarity: Assumes stable cointegration; structural breaks can invalidate the model.

    Execution Assumptions:

        No transaction costs, slippage, or borrowing constraints.

        Positions fully filled at historical close prices.

    Risk Management: Position sizing and stop-loss levels are fixed; no volatility scaling.

7. Potential Improvements

    Hedging Ratio: Use regression slope (ββ) for more accurate hedging.

    Dynamic Thresholds: Optimize z-score entry/exit levels using historical data.

    Expanded Pair Universe: Automatically identify cointegrated pairs via Engle-Granger or Johansen tests.

    Transaction Costs: Incorporate realistic execution costs to evaluate profitability.

    Risk Management: Introduce volatility-based sizing, drawdown limits, and capital allocation rules.

    Live Trading: Integrate with a broker API (e.g., Interactive Brokers) for real-time execution.

Summary

This repository implements a fully functional pairs trading strategy using cointegration, z-score-based mean reversion, and backtesting. It provides a framework for further research, parameter optimization, and eventual deployment in live trading environments.
