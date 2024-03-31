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


# 定义策略
class DynamicMACDStrategy(bt.Strategy):
    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close,
                                       period_me1=self.params.fast,
                                       period_me2=self.params.slow,
                                       period_signal=self.params.signal)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:  # 没有持仓
            if self.crossover > 0:  # MACD线上穿信号线
                self.buy()
        elif self.crossover < 0:  # 已有持仓且MACD线下穿信号线
            self.sell()


if __name__ == '__main__':
    ibstore = IBStore('127.0.0.1', 4002, clientId=1)
    # df = ibstore.get_data('NVDA')
    df = ibstore.get_data('AAPL')

    # Ensure the 'date' column is in the correct datetime format
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Load data into Backtrader
    data = bt.feeds.PandasData(dataname=df)

    # Initialize and run Cerebro
    cerebro = bt.Cerebro(stdstats=True, cheat_on_open=True, optreturn=False)
    cerebro.optstrategy(DynamicMACDStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.broker.set_cash(100000)
    # cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(data)  # 确保这里的data是bt.feeds对象，不是pandas DataFrame
    result = cerebro.run()

    best_params = None
    best_sharpe = float('-inf')  # 初始化为负无穷大

    for run in result:
        for strategy in run:
            sharpe = strategy.analyzers.sharpe.get_analysis()['sharperatio']
            params = strategy.params
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params

    print(f"Best Sharpe Ratio: {best_sharpe}")
    print(f"With Parameters: Fast={best_params.fast}, Slow={best_params.slow}, Signal={best_params.signal}")
    cerebro.plot()
