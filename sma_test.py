from datetime import datetime
import backtrader as bt
from ib_insync import IB, Stock, util
import pandas as pd

class IBStore:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)

    def get_data(self, symbol, durationStr='1 Y', barSizeSetting='1 day', whatToShow='MIDPOINT'):
        contract = Stock(symbol, 'SMART', 'USD')
        bars = self.ib.reqHistoricalData(
            contract, endDateTime='', durationStr=durationStr,
            barSizeSetting=barSizeSetting, whatToShow=whatToShow, useRTH=True)
        df = util.df(bars)
        df.to_csv('/Users/eleme/Github/Quant/' + symbol + '.csv', sep=',', index=False, header=True)
        return df

# Define Backtrader Strategy
class MaCrossStrategy(bt.Strategy):
    params = (('pfast', 10), ('pslow', 30),)

    def __init__(self):
        sma1 = bt.indicators.SMA(self.data.close, period=self.params.pfast, plotname="10 day moving average")
        sma2 = bt.indicators.SMA(self.data.close, period=self.params.pslow, plotname="30 day moving average")

        self.crossover = bt.indicators.CrossOver(sma1, sma2)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # Golden cross buy signal
                self.buy()
        elif self.crossover < 0:  # Death cross sell signal
            self.sell()

# Class for SMA Crossover strategy
class SmaCross(bt.Strategy):
    params = dict(pfast=13, pslow=25)

    # Define trading strategy
    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)
        sma2 = bt.ind.SMA(period=self.p.pslow)
        self.crossover = bt.ind.CrossOver(sma1, sma2)

        # Custom trade tracking
        self.trade_data = []

    # Execute trades
    def next(self):
        # Trading the entire portfolio
        size = int(self.broker.get_cash() / self.data.close[0])

        if not self.position:
            if self.crossover > 0:
                self.buy(size=size)
                self.entry_bar = len(self)  # Record entry bar index
        elif self.crossover < 0:
            self.close()

    # Record trade details
    def notify_trade(self, trade):
        if trade.isclosed:
            exit_bar = len(self)
            holding_period = exit_bar - self.entry_bar
            trade_record = {
                'entry': self.entry_bar,
                'exit': exit_bar,
                'duration': holding_period,
                'profit': trade.pnl
            }
            self.trade_data.append(trade_record)

    # Caclulating holding periods
    def stop(self):
        # Calculate and print average holding periods
        total_holding = sum([trade['duration'] for trade in self.trade_data])
        total_trades = len(self.trade_data)
        avg_holding_period = round(total_holding / total_trades) if total_trades > 0 else 0

        # Calculating for winners and losers separately
        winners = [trade for trade in self.trade_data if trade['profit'] > 0]
        losers = [trade for trade in self.trade_data if trade['profit'] < 0]
        avg_winner_holding = round(sum(trade['duration'] for trade in winners) / len(winners))if winners else 0
        avg_loser_holding = round(sum(trade['duration'] for trade in losers) / len(losers)) if losers else 0

        # Display average holding period statistics
        print('Average Holding Period:', avg_holding_period)
        print('Average Winner Holding Period:', avg_winner_holding)
        print('Average Loser Holding Period:', avg_loser_holding)


if __name__ == '__main__':
    ibstore = IBStore('127.0.0.1', 4002, clientId=1)
    df = ibstore.get_data('NVDA')
    # df = ibstore.get_data('AAPL')

    # Ensure the 'date' column is in the correct datetime format
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Load data into Backtrader
    data = bt.feeds.PandasData(dataname=df)

    # Initialize and run Cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)
    cerebro.broker.set_cash(100000)
    # cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(data)
    cerebro.run()
    cerebro.plot()
