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


class ImprovedMACDStrategy(bt.Strategy):
    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9),
        ('order_percentage', 0.95),  # 买入资金比例
        ('stop_loss_percentage', 0.95),  # 止损比例
        ('take_profit_percentage', 1.05),  # 止盈比例
        ('partial_sell_percentage', 0.5),  # 部分卖出比例
        ('profit_threshold', 1.02),  # 盈利阈值，达到则部分卖出
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close,
                                       period_me1=self.params.fast,
                                       period_me2=self.params.slow,
                                       period_signal=self.params.signal)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.stop_price = self.buy_price * self.params.stop_loss_percentage
                self.limit_price = self.buy_price * self.params.take_profit_percentage
            self.order = None

    def next(self):
        if self.order:
            return  # 如果有未完成的订单，则不执行任何操作

        if not self.position:  # 没有持仓时
            if self.crossover > 0:  # MACD线上穿信号线，买入信号
                self.order = self.buy(size=(self.broker.get_cash() / self.data.close[0]) * self.params.order_percentage)
        else:  # 已有持仓时
            if self.data.close[0] / self.buy_price > self.params.profit_threshold:
                # 达到盈利阈值，部分卖出
                self.order = self.sell(size=self.position.size * self.params.partial_sell_percentage)
            elif self.crossover < 0 or self.data.close[0] < self.stop_price or self.data.close[0] > self.limit_price:
                # MACD线下穿信号线，或触发止损止盈，全仓卖出
                self.order = self.close()


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
    cerebro.optstrategy(ImprovedMACDStrategy)
    # cerebro.optstrategy(ImprovedMACDStrategy, fast=range(10, 15), slow=range(20, 30), signal=range(5, 10))
    # Best Sharpe Ratio: 0.801877924498146
    # With Parameters: Fast=10, Slow=27, Signal=5
    # cerebro.optstrategy(ImprovedMACDStrategy, fast=10, slow=27, signal=5)
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
