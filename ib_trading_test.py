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
#
#
# class MeanReversionStrategy(bt.Strategy):
#     params = (('period', 20), ('devfactor', 2), ('atr_period', 14), ('risk_percent', 1.0),)
#
#     def __init__(self):
#         self.boll = bt.indicators.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#
#     def next(self):
#         if not self.position:  # No open positions
#             if self.data.close[0] < self.boll.lines.bot[0]:  # Price below lower Bollinger Band
#                 atr_value = self.atr[0]
#                 risk_per_share = atr_value * self.params.risk_percent
#                 size = self.broker.getcash() / (risk_per_share * self.data.close[0])
#                 self.buy(size=size)
#         else:  # Have open positions
#             if self.data.close[0] > self.boll.lines.top[0]:  # Price above upper Bollinger Band
#                 self.close()  # Close position
#
# # 你的量化交易策略主要是依赖于布林带（Bollinger Bands）来识别价格的超买和超卖区域。这种策略在高波动性市场中效果不错，因为价格经常触及布林带的上下边界。然而，在单向趋势市场中，这样的策略可能会错失持续的趋势。
# #
# # 以下是对你的代码进行的几点优化建议：
# #
# # 增加趋势跟踪指标：考虑结合使用趋势跟踪指标，比如移动平均线、MACD（Moving Average Convergence Divergence）或者DMI（Directional Movement Index），这样可以帮助识别和持有趋势。
# #
# # 动态仓位管理：你当前的策略在进入交易时使用了基于ATR的固定风险百分比来计算仓位大小。你可以增加一个逻辑来调整现有仓位的大小，如果趋势持续你可能想增加你的仓位。
# #
# # 利润保护：加入止盈或移动止损机制，以保护在趋势中累积的利润。
# #
# # 市场状态判断：可以根据历史波动率、成交量等因素动态调整你的策略参数，比如布林带的周期和偏差、ATR的周期等。
# class OptimizedMeanReversionStrategy(bt.Strategy):
#     params = (
#         ('period', 20),
#         ('devfactor', 2),
#         ('atr_period', 14),
#         ('risk_percent', 1.0),
#         ('sma_period', 50),  # 新增简单移动平均线周期
#     )
#
#     def __init__(self):
#         self.boll = bt.indicators.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)  # 简单移动平均线
#         self.order = None
#
#     def next(self):
#         if self.order:  # 检查是否有未完成的订单
#             return
#
#         # 检查趋势
#         if self.data.close[0] > self.sma[0]:  # 简单移动平均线上升趋势
#             if not self.position:
#                 if self.data.close[0] < self.boll.lines.bot[0]:  # 价格在布林带下轨以下
#                     atr_value = self.atr[0]
#                     risk_per_share = atr_value * self.params.risk_percent
#                     size = self.broker.getcash() / (risk_per_share * self.data.close[0])
#                     self.order = self.buy(size=size)
#         elif self.data.close[0] < self.sma[0]:  # 简单移动平均线下降趋势
#             if self.position:
#                 if self.data.close[0] > self.boll.lines.top[0]:  # 价格在布林带上轨以上
#                     self.order = self.close()  # 平仓
#
#         if self.position:  # 如果持有仓位，加入移动止损保护利润
#             if self.data.close[0] < self.sma[0]:  # 如果跌破移动平均线，则卖出
#                 self.order = self.close()
#
# # 似乎交易策略依然未能在图表所示的上涨趋势中执行任何买入操作。这可能意味着买入逻辑条件可能没有得到满足，或者可能存在代码中的逻辑错误。为了更好地利用趋势并进行交易，我们可以采取以下几步优化策略：
# #
# # 使用更多的趋势指标：除了布林带外，可以考虑使用其他趋势跟踪指标，如MACD或者DMI来帮助确认趋势的存在。
# #
# # 调整买入卖出条件：如果股价一直在上升，考虑放宽买入条件，比如当股价回落至布林带中轨附近时就买入。
# #
# # 动态仓位调整：基于市场波动性和当前持仓情况动态调整仓位大小，可以帮助抓住趋势并在必要时降低风险。
# #
# # 止损和止盈：设定明确的止损和止盈点，以锁定利润并限制亏损。
# #
# # 优化参数：对策略的参数进行优化，找出历史表现最佳的参数组合。
# class OptimizedTrendFollowingStrategy(bt.Strategy):
#     params = (
#         ('period', 20),
#         ('devfactor', 2),
#         ('atr_period', 14),
#         ('risk_percent', 1.0),
#         ('sma_period', 50),
#     )
#
#     def __init__(self):
#         self.boll = bt.indicators.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
#         self.macd = bt.indicators.MACD(self.data.close)
#         self.order = None
#
#     def log(self, txt):
#         ''' Logging function '''
#         print(txt)
#
#     def next(self):
#         if self.order:
#             return
#
#         if self.macd > 0 and self.data.close > self.sma:  # 确认上升趋势
#             if not self.position:
#                 size = self.broker.getcash() / self.data.close
#                 self.order = self.buy(size=size)
#                 self.log('BUY CREATE, Size: %.2f' % size)
#         elif self.macd < 0 or self.data.close < self.sma:  # 确认下降趋势或趋势结束
#             if self.position:
#                 self.order = self.sell(size=self.position.size)
#                 self.log('SELL CREATE, Size: %.2f' % self.position.size)
#
# # 我们可以对策略进行如下的优化：
# #
# # 使用自适应的参数：根据股票的波动性动态调整策略的关键参数，如布林带的周期和宽度、移动平均线的周期等。
# # 使用百分比风险模型来动态计算买入的仓位大小：我们可以定义一个风险值，比如决定每笔交易最多只能损失账户总值的一定比例。
# # 仓位大小计算考虑到ATR：ATR指标能够帮助我们了解当前市场的波动性，我们可以使用它来调整我们的止损距离，进而计算仓位。
# # 以下是包含自适应参数和动态仓位算法的代码示例：
# class DynamicParamsTrendFollowingStrategy(bt.Strategy):
#     params = (
#         ('risk_per_trade', 0.01),  # 每笔交易风险1%
#         ('sma_period', 50),
#         ('atr_period', 14),
#         ('macd1', 12),
#         ('macd2', 26),
#         ('macdsig', 9),
#     )
#
#     def __init__(self):
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.macd = bt.indicators.MACD(
#             self.data.close,
#             period_me1=self.params.macd1,
#             period_me2=self.params.macd2,
#             period_signal=self.params.macdsig
#         )
#         self.order = None
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         if self.order:  # 确保没有挂起的订单
#             return
#
#         # 计算ATR为止损点，动态调整买入仓位大小
#         atr_value = self.atr[0]
#         risk_per_share = atr_value * self.params.risk_per_trade
#         position_size = self.broker.getcash() * self.params.risk_per_trade / risk_per_share
#
#         # 确定是否处于上升趋势
#         if self.macd > 0 and self.data.close > self.sma:
#             if not self.position:
#                 self.order = self.buy(size=position_size)
#                 self.log('BUY CREATE, Size: %.2f' % position_size)
#
#         # 确定是否处于下降趋势或趋势结束
#         elif self.position and (self.macd < 0 or self.data.close < self.sma):
#             self.order = self.sell(size=self.position.size)
#             self.log('SELL CREATE, Size: %.2f' % self.position.size)
#
#
# # 从你的图表中可以看出，尽管有策略在执行，但没有任何交易被触发。这可能是因为策略的条件设置得太过保守，或者策略的逻辑不适用于当前的市场条件。为了解决这个问题，我们可以采取以下策略：
# #
# # 简化交易信号：将交易信号简化为只基于一个或两个关键指标，这样可以更容易地触发交易。
# #
# # 调整指标参数：基于当前市场的行为来调整指标参数，例如调整MACD的快线、慢线和信号线的周期。
# #
# # 加入止损和止盈：在策略中加入固定的止损和止盈水平或者是一个跟踪止损，以保护资本并锁定利润。
# #
# # 引入其他指标：例如RSI（相对强弱指数）或Stochastic（随机振荡指数）可以帮助识别超买和超卖的条件。
# class AdaptiveStrategy(bt.Strategy):
#     params = (
#         ('risk_per_trade', 0.01),  # 每笔交易风险1%
#         ('sma_period', 50),
#         ('atr_period', 14),
#         ('macd_fast', 12),
#         ('macd_slow', 26),
#         ('macd_signal', 9),
#         ('rsi_period', 14),
#         ('rsi_overbought', 70),
#         ('rsi_oversold', 30),
#         ('stop_loss_atr', 2)
#     )
#
#     def __init__(self):
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.macd = bt.indicators.MACD(
#             self.data.close,
#             period_me1=self.params.macd_fast,
#             period_me2=self.params.macd_slow,
#             period_signal=self.params.macd_signal
#         )
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.order = None
#         self.buy_price = None
#         self.stop_loss = None
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         if self.order:  # 确保没有挂起的订单
#             return
#
#         if not self.position:  # 如果当前没有持仓
#             if self.macd > 0 and self.rsi < self.params.rsi_oversold:
#                 # 计算买入仓位大小
#                 position_size = (self.broker.getcash() / self.data.close[0]) * self.params.risk_per_trade
#                 self.order = self.buy(size=position_size)
#                 self.buy_price = self.data.close[0]
#                 self.stop_loss = self.buy_price - self.atr[0] * self.params.stop_loss_atr
#                 self.log('BUY CREATE, Size: %.2f, Price: %.2f, Stop Loss: %.2f' % (
#                 position_size, self.buy_price, self.stop_loss))
#
#         else:  # 如果当前持有仓位
#             if self.macd < 0 or self.rsi > self.params.rsi_overbought:
#                 self.order = self.sell(size=self.position.size)
#                 self.log('SELL CREATE, Size: %.2f, Price: %.2f' % (self.position.size, self.data.close[0]))
#
#             # 更新止损
#             if self.data.close[0] < self.stop_loss:
#                 self.order = self.close()  # 止损卖出
#                 self.log('STOP LOSS HIT, Price: %.2f' % self.data.close[0])
#
#
# # 看起来您希望有一个能够在不同市场条件下有效触发交易的策略。我将提供一个新的策略示例，这个策略将使用以下规则：
# #
# # 使用简化的趋势跟踪逻辑，基于移动平均线的位置，买入股票当股价在移动平均线之上，并在股价下穿移动平均线时卖出。
# #
# # 动态调整仓位大小，基于账户总资产的一定比例，与ATR结合以考虑市场波动性。
# #
# # 引入ATR作为止损指标，这有助于我们管理风险，止损距离将设置为当前ATR的多个倍数。
# #
# # 考虑资金管理，限制每笔交易风险为账户余额的固定百分比。
# class DynamicTrendFollowingStrategy(bt.Strategy):
#     params = (
#         ('sma_period', 50),
#         ('atr_period', 14),
#         ('risk_per_trade', 0.01),  # 每笔交易的风险为1%
#         ('stop_loss_atr', 2),  # 止损设置为ATR的2倍
#     )
#
#     def __init__(self):
#         self.sma = bt.indicators.SMA(period=self.params.sma_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.order = None
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         if self.order:  # 如果存在未决订单，不执行操作
#             return
#
#         # 当前账户价值和每笔交易风险量
#         current_value = self.broker.getvalue()
#         risk_amount = current_value * self.params.risk_per_trade
#
#         # 计算ATR值用于确定仓位大小
#         atr_value = self.atr[0]
#         stop_loss_price = atr_value * self.params.stop_loss_atr
#
#         # 计算可买入的股票数量
#         size = risk_amount / stop_loss_price
#
#         # 如果当前没有持仓，且股价高于移动平均线，买入
#         if not self.position and self.data.close > self.sma:
#             self.order = self.buy(size=size)
#             self.log('BUY CREATE, Size: %.2f' % size)
#
#         # 如果持仓，且股价跌破移动平均线，卖出
#         elif self.position and self.data.close < self.sma:
#             self.order = self.close()  # 平仓
#             self.log('SELL CREATE, Size: %.2f' % size)
#
# # 针对剧烈波动的市场，可以考虑以下策略优化：
# #
# # 引入振荡指标：使用如RSI或随机振荡器（Stochastic Oscillator）等振荡指标来识别过度买入或卖出的情况。
# #
# # 动态调整移动平均线周期：在市场波动性大时，缩短移动平均线的周期以更快地反应价格变化；在市场稳定时，增加周期以过滤掉噪音。
# #
# # 使用波动性指标：比如平均真实范围（ATR）来动态设置止损和止盈点，可以根据当前市场波动性来调整这些阈值。
# #
# # 资金管理：可能需要更精细的资金管理方法，比如在连续盈利后增加交易规模，在亏损后减小交易规模。
# #
# # 多周期分析：同时监控不同时间周期的指标，比如短期内的强势和长期内的趋势。
# class VolatilityAdaptiveStrategy(bt.Strategy):
#     params = (
#         ('fast_sma_period', 20),  # 较短周期的SMA
#         ('slow_sma_period', 50),  # 较长周期的SMA
#         ('rsi_period', 14),
#         ('rsi_overbought', 70),
#         ('rsi_oversold', 30),
#         ('atr_period', 14),
#         ('atr_multiplier', 3),  # ATR乘数定义止损点
#         ('risk_per_trade', 0.01),
#     )
#
#     def __init__(self):
#         self.fast_sma = bt.indicators.SMA(period=self.params.fast_sma_period)
#         self.slow_sma = bt.indicators.SMA(period=self.params.slow_sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.order = None
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         if self.order:  # 确保没有挂起的订单
#             return
#
#         # 当前账户价值和每笔交易风险量
#         current_value = self.broker.getvalue()
#         risk_amount = current_value * self.params.risk_per_trade
#
#         # 计算ATR值用于确定仓位大小和止损点
#         atr_value = self.atr[0]
#         position_size = risk_amount / (atr_value * self.params.atr_multiplier)
#
#         # 确定入市信号
#         if not self.position:  # 如果当前没有持仓
#             if (self.data.close > self.fast_sma and
#                     self.data.close > self.slow_sma and
#                     self.rsi < self.params.rsi_oversold):
#                 self.order = self.buy(size=position_size)
#                 self.log('BUY CREATE, Size: %.2f' % position_size)
#
#         # 确定出市信号
#         elif self.position:  # 如果当前持有仓位
#             if (self.data.close < self.fast_sma or
#                     self.data.close < self.slow_sma or
#                     self.rsi > self.params.rsi_overbought):
#                 self.order = self.close()  # 平仓
#                 self.log('SELL CREATE, Size: %.2f' % position_size)
#
#
#
# # 需要进一步的优化以便在剧烈波动时进行交易。以下是针对您的策略提出的一些改进点：
# #
# # 交叉验证移动平均线：当快速移动平均线（SMA）从下方穿越慢速移动平均线时买入，当从上方穿越时卖出，可以更快地响应市场变化。
# #
# # 动态仓位调整：基于ATR动态调整仓位大小，以适应市场波动。
# #
# # 引入止损和止盈：使用ATR来设定动态止损和止盈，可以更好地管理风险和利润。
# #
# # 增加条件确认：确认买入卖出条件时，可以加入一些额外的确认，如确认当前价格是否真的穿越了移动平均线。
# #
# # 添加滤网：为了避免在没有明确趋势的市场中交易，您可以添加一些滤网条件，如只有当RSI处于中立区域时才进行交易。
# #
# # 这个策略现在使用了SMA交叉验证来产生交易信号，并且使用ATR来动态设置止损和止盈点。
# class VolatilityAdaptiveStrategy(bt.Strategy):
#     params = (
#         ('fast_sma_period', 20),
#         ('slow_sma_period', 50),
#         ('rsi_period', 14),
#         ('rsi_overbought', 70),
#         ('rsi_oversold', 30),
#         ('atr_period', 14),
#         ('atr_multiplier', 3),
#         ('risk_per_trade', 0.01),
#     )
#
#     def __init__(self):
#         self.fast_sma = bt.indicators.SMA(period=self.params.fast_sma_period)
#         self.slow_sma = bt.indicators.SMA(period=self.params.slow_sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
#         self.order = None
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         if self.order:
#             return
#
#         current_value = self.broker.getvalue()
#         risk_amount = current_value * self.params.risk_per_trade
#         atr_value = self.atr[0]
#         position_size = risk_amount / (atr_value * self.params.atr_multiplier)
#
#         if not self.position:
#             if self.crossover > 0:
#                 self.order = self.buy(size=position_size)
#                 self.log('BUY CREATE, Size: %.2f' % position_size)
#         elif self.position:
#             if self.crossover < 0:
#                 self.order = self.close()
#                 self.log('SELL CREATE, Size: %.2f' % position_size)
#
#             if self.data.close[0] < self.position.price - atr_value * self.params.atr_multiplier:
#                 self.close()  # 止损
#                 self.log('STOP LOSS TRIGGERED, Size: %.2f' % position_size)
#
#             if self.data.close[0] > self.position.price + atr_value * self.params.atr_multiplier:
#                 self.close()  # 止盈
#                 self.log('TAKE PROFIT TRIGGERED, Size: %.2f' % position_size)
#
#
# # 策略在波动性较大的市场中表现不佳，只执行了一次买入操作且最终亏损。要改进这种情况，您可以考虑以下几个方面的策略调整：
# #
# # 更敏感的趋势跟踪：减少SMA的周期，使用更短期的移动平均线来更快地响应价格变化。
# #
# # 使用更多的入市和离市信号：除了SMA交叉外，还可以加入其他指标，如MACD、布林带等。
# #
# # 动态止损和止盈：基于波动率调整止损和止盈水平。
# #
# # 分批进出：在确认趋势后，可以分批进入市场，而不是一次性全仓操作。
# #
# # 添加其他类型的指标：比如加入动量指标或波动率指标，来提供关于市场状态的更多信息。
# #
# # 时间窗口优化：在更短的时间窗口内评估市场条件，而不是只依赖于日线数据。
# #
# # 现在，让我们重新设计策略并增加一个更加灵敏的入市和离市机制，以及基于波动性的动态止损：
#
# class DynamicTrendFollowingStrategy2(bt.Strategy):
#     params = (
#         ('sma_short_period', 15),  # 较短周期的SMA，更快反应
#         ('sma_long_period', 30),  # 较长周期的SMA
#         ('atr_period', 14),
#         ('atr_dist', 2),  # ATR距离乘数，用于动态止损
#         ('risk_per_trade', 0.02),  # 每笔交易的风险为2%
#     )
#
#     def __init__(self):
#         self.sma_short = bt.indicators.SMA(period=self.params.sma_short_period)
#         self.sma_long = bt.indicators.SMA(period=self.params.sma_long_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.crossup = bt.indicators.CrossOver(self.sma_short, self.sma_long)  # 短周期穿越长周期向上
#         self.crossdown = bt.indicators.CrossDown(self.sma_short, self.sma_long)  # 短周期穿越长周期向下
#         self.order = None
#
#     def next(self):
#         cash = self.broker.get_cash()
#         atr_value = self.atr[0]
#         position_size = (cash * self.params.risk_per_trade) / (atr_value * self.params.atr_dist)
#
#         if not self.position:
#             if self.crossup > 0:  # 如果短周期SMA穿越长周期SMA向上
#                 self.order = self.buy(size=position_size)
#         else:
#             if self.crossdown < 0:  # 如果短周期SMA穿越长周期SMA向下
#                 self.order = self.sell(size=self.position.size)
#             else:
#                 # 动态止损
#                 if self.data.close[0] < (self.order.executed.price - atr_value * self.params.atr_dist):
#                     self.order = self.sell(size=self.position.size)
#
#
# # 一种可能的策略是结合多种指标以及对价格行为的直接分析来制定交易决策。这可以帮助策略更好地把握波动市场中的交易机会。
# #
# # 我们可以设计一个结合了价格行为、移动平均线交叉以及动量指标（如RSI或Stochastic）的策略。这种策略可以通过识别趋势的强度和市场的超买或超卖状态来改善交易点。
# class ImprovedStrategy(bt.Strategy):
#     params = (
#         ('sma_short_period', 15),
#         ('sma_long_period', 30),
#         ('rsi_period', 14),
#         ('rsi_overbought', 70),
#         ('rsi_oversold', 30),
#         ('atr_period', 14),
#         ('atr_multiplier', 2),
#         ('risk_per_trade', 0.01),
#     )
#
#     def __init__(self):
#         self.sma_short = bt.indicators.SMA(period=self.params.sma_short_period)
#         self.sma_long = bt.indicators.SMA(period=self.params.sma_long_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.crossover = bt.indicators.CrossOver(self.sma_short, self.sma_long)
#
#     def next(self):
#         # 如果没有持仓，考虑买入
#         if not self.position:
#             # 股价在短期SMA上方且SMA短期高于长期，RSI不在超买状态
#             if self.data.close > self.sma_short and self.crossover > 0 and self.rsi < self.params.rsi_overbought:
#                 size = (self.broker.get_cash() * self.params.risk_per_trade) / (self.atr[0] * self.params.atr_multiplier)
#                 self.buy(size=size)
#
#         # 如果已经持有仓位，考虑卖出
#         elif self.position:
#             # 股价跌破长期SMA或RSI进入超买状态
#             if self.data.close < self.sma_long or self.rsi > self.params.rsi_overbought:
#                 self.sell(size=self.position.size)
#             # 动态止损，如果股价跌破最近的低点 - ATR
#             elif self.data.close[0] < self.data.low[-1] - self.atr[0] * self.params.atr_multiplier:
#                 self.sell(size=self.position.size)
#
# # 现有的交易策略在单边上涨趋势中表现不佳。这表明需要对策略做进一步的优化以便在多种市场情况下均能表现良好。我们可以考虑以下几个方向进行优化：
# #
# # 更快的响应机制：缩短SMA的周期，使策略能够快速响应市场变化。
# # 动态仓位调整：在明确的趋势中增加仓位，而在趋势不明显或者反转信号出现时减少或清仓。
# # 动态止损和止盈：基于市场波动性调整止损和止盈点，例如使用ATR进行动态调整。
# # 利用价格行为：考虑在价格接近重要的技术水平（如前高/前低、支撑/阻力位）时进入市场。
# # 引入其他技术指标：考虑使用更复杂的技术指标，比如布林带或者斐波那契回撤水平来辅助决策。
# # 这个策略现在更侧重于趋势追踪，并且通过使用RSI限制在超买条件下的购买。同时，通过一个简单的移动平均线和ATR调整的滞后止损来尝试保护盈利。注意，这段代码仍然是一个基础模板，需要根据您实际的回测结果来调整参数。在真实市场交易中使用之前，请确保进行充分的历史回测以及前瞻性测试。
# class OptimizedStrategy(bt.Strategy):
#     params = {
#         'sma_period': 10,
#         'rsi_period': 14,
#         'rsi_upper': 65,
#         'rsi_lower': 35,
#         'atr_period': 14,
#         'risk_per_trade': 0.02,
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.in_position = False
#
#     def log(self, txt):
#         print(txt)
#
#     def next(self):
#         atr_value = self.atr[0]
#         if not self.in_position:
#             if self.data.close > self.sma and self.rsi < self.params.rsi_upper:
#                 size = (self.broker.cash * self.params.risk_per_trade) / atr_value
#                 self.buy(size=size)
#                 self.in_position = True
#         else:
#             if self.data.close < self.sma or self.rsi > self.params.rsi_upper:
#                 self.sell(size=self.position.size)
#                 self.in_position = False
#             elif self.data.close < self.data.close[-1] - atr_value * 2:  # Trailing stop
#                 self.sell(size=self.position.size)
#                 self.in_position = False
#
#
# # 策略需要能够更敏感地反应波动，并在趋势变化时及时调整仓位。我们可以引入以下策略优化点：
# #
# # 调整入市条件：当股价高于快速SMA时考虑买入，但也增加其他条件如股价相对于快速SMA的位置或股价的变化率。
# #
# # 加入逆向指标：比如当RSI过低时考虑买入，过高时考虑卖出。
# #
# # 动态止损：不仅仅使用ATR固定值，还可以参考最近的高点或低点来设定止损点。
# #
# # 利用振荡器指标：比如布林带，可以在股价触及上轨时考虑卖出，在触及下轨时考虑买入。
# #
# # 短线交易：考虑使用较短的时间框架数据，比如小时图或分钟图，以更快地捕捉市场的微观波动。
#
# # 这段代码创建了一个趋势跟踪策略，它在股价上升到快速SMA线上方且RSI指标不是过高时买入，而当股价跌破快速SMA线下方或RSI指标过高时卖出。此外，这个策略使用了一个尾随止损来保护利润。
# class ImprovedTrendFollowingStrategy(bt.Strategy):
#     params = {
#         'sma_period': 10,
#         'rsi_period': 14,
#         'atr_period': 14,
#         'risk_per_trade': 0.02,
#         'fast_track_multiplier': 1.5,
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.fast_track_high = self.sma * (1 + self.params.fast_track_multiplier / 100)
#         self.fast_track_low = self.sma * (1 - self.params.fast_track_multiplier / 100)
#
#     def next(self):
#         if not self.position:
#             if self.data.close > self.fast_track_high and self.rsi < self.params.rsi_period:
#                 size = (self.broker.get_cash() * self.params.risk_per_trade) / self.atr[0]
#                 self.buy(size=size)
#         elif self.data.close < self.fast_track_low or self.rsi > 100 - self.params.rsi_period:
#             self.sell(size=self.position.size)
#         elif self.data.close[0] < self.data.close[-1] - self.atr[0] * 2:  # Trailing stop
#             self.sell(size=self.position.size)
#
# # 一个可能的策略是利用趋势跟随和动量指标的结合。看来需要一个更为积极的买入逻辑和更灵敏的卖出信号，同时考虑波动性和价格动量。以下是一个优化的策略，它使用了这些概念：
# #
# # 趋势识别：通过价格相对于快速移动平均线的位置来识别趋势。
# # 动量确认：使用RSI等动量指标来确认买入卖出信号。
# # 动态止损：使用ATR来设置动态止损距离。
# # 盈利保护：一旦达到某一盈利比例，启动移动止损以保护利润。
# # 这个策略更注重趋势跟随，当RSI显示足够强的动量时进行买入，并在动量减弱时卖出。此外，如果股价达到较高的盈利水平，则通过移动止损来保护利润。
# class AdaptiveTrendFollowingStrategy(bt.Strategy):
#     params = {
#         'sma_period': 10,
#         'rsi_period': 14,
#         'rsi_entry': 60,  # 动量确认的RSI入市门槛
#         'rsi_exit': 40,  # 动量确认的RSI出市门槛
#         'atr_period': 14,
#         'profit_multiplier': 5,  # 盈利倍数来设置止盈
#         'risk_per_trade': 0.01,
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SMA(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#
#     def next(self):
#         cash = self.broker.get_cash()
#         atr_value = self.atr[0]
#         position_size = (cash * self.params.risk_per_trade) / atr_value
#
#         if not self.position:
#             if self.data.close > self.sma and self.rsi > self.params.rsi_entry:
#                 self.buy(size=position_size)
#         else:
#             if self.rsi < self.params.rsi_exit:
#                 self.sell(size=self.position.size)
#             elif (self.data.close[0] > self.position.price + atr_value * self.params.profit_multiplier):
#                 # 如果价格超过买入价格一定倍数的ATR，则启动移动止损
#                 self.sell(size=self.position.size)
#
# # 将针对提供的具体情况（AAPL和NVDA的走势）设计一个更为复杂的策略。这个策略将结合趋势跟踪和反转信号来尝试在低点买入、高点卖出。
# #
# # 考虑到Backtrader框架中的限制，我们不能直接处理您的CSV文件，但是可以假设它们已经被加载为数据源。我将提供一个更为精细的策略样本代码，它将尝试根据以下原则操作：
# #
# # 当股价在短期SMA之上并且RSI表明股票没有被超买时买入。
# # 当股价在短期SMA之下或者RSI表明股票被超买时卖出。
# # 在达到一定盈利后，使用动态的止盈和尾随止损来保护利润。
# # 这个策略使用了尾随止损（trailing stop）机制，它将在价格上涨到一定程度后提高止损价格，从而在价格反转时保护盈利。这是为了防止市场突然的反转导致利润的流失。
# #
# # 请注意，在实际应用中，您需要根据AAPL和NVDA的数据来优化参数。这可能包括调整RSI的超买和超卖阈值、ATR乘数以及止盈和止损水平。每次交易之前应该重新计算这些值，以适应当前的市场条件。
# class AdaptiveTrendFollowingStrategy2(bt.Strategy):
#     params = {
#         'sma_period': 10,
#         'rsi_period': 14,
#         'atr_period': 14,
#         'risk_per_trade': 0.02,
#         'trail_stop_atr': 2,
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SMA(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.buy_signal = bt.And(self.data.close > self.sma, self.rsi < 70)
#         self.sell_signal = bt.Or(self.data.close < self.sma, self.rsi > 70)
#
#     def next(self):
#         atr_value = self.atr[0]
#         if not self.position and self.buy_signal:
#             size = (self.broker.get_cash() * self.params.risk_per_trade) / atr_value
#             self.buy(size=size)
#
#         if self.position and self.sell_signal:
#             self.sell(size=self.position.size)
#
#         if self.position and self.data.close > self.position.price + atr_value * self.params.trail_stop_atr:
#             # If the price is higher than the buying price plus two times of ATR
#             # it updates the stop price to a new level (trailing stop)
#             self.sell(size=self.position.size, exectype=bt.Order.StopTrail, trailamount=atr_value)
#
#
# from backtrader.indicators import ExponentialMovingAverage, Stochastic
#
# # 我们需要一个策略能够在多种市场条件下均表现良好。对于上涨趋势中的股票如NVDA，策略需要能够持续跟踪趋势而不是频繁交易；对于波动较大的股票如AAPL，策略则需要能够识别并利用波动带来的交易机会。下面是一个尝试平衡这些需求的改进策略：
# # 这个策略使用EMA和Stochastic指标来判定入市和离市时机。EMA提供趋势方向的信息，而Stochastic则用来识别潜在的转折点。ATR用于动态设定止损和止盈。策略在价格向有利方向移
#
# class CombinedStrategy(bt.Strategy):
#     params = {
#         'fast_ema_period': 12,
#         'slow_ema_period': 26,
#         'stochastic_period': 14,
#         'stochastic_upper': 80,
#         'stochastic_lower': 20,
#         'atr_period': 14,
#         'risk_per_trade': 0.02,
#         'profit_lock_multiplier': 3,  # 锁定盈利的ATR倍数
#     }
#
#     def __init__(self):
#         self.fast_ema = ExponentialMovingAverage(period=self.params.fast_ema_period)
#         self.slow_ema = ExponentialMovingAverage(period=self.params.slow_ema_period)
#         self.stochastic = Stochastic(period=self.params.stochastic_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.order = None
#         self.initial_stop_loss = None
#
#     def next(self):
#         if self.order:
#             return
#
#         if not self.position:
#             if self.fast_ema > self.slow_ema and self.stochastic < self.params.stochastic_upper:
#                 size = (self.broker.get_cash() * self.params.risk_per_trade) / self.atr[0]
#                 self.order = self.buy(size=size)
#                 self.initial_stop_loss = self.data.close[0] - self.atr[0] * self.params.profit_lock_multiplier
#
#         elif self.position:
#             if self.fast_ema < self.slow_ema or self.stochastic > self.params.stochastic_lower:
#                 self.order = self.close()
#             else:
#                 # If the price moves in our favor, trail the stop loss to lock in profit
#                 if self.data.close[0] > self.position.price + self.atr[0] * self.params.profit_lock_multiplier:
#                     self.initial_stop_loss += self.atr[0] * self.params.profit_lock_multiplier
#
#                 # Check if the stop loss should be hit
#                 if self.data.close[0] < self.initial_stop_loss:
#                     self.order = self.close()
#
# # 为了改进策略，以便捕捉波动市场中的利润机会，让我们考虑以下几个策略调整：
# #
# # 更多买卖信号的结合：不仅基于SMA和RSI，而且可以结合其他指标，如MACD或Volume来提供买卖信号。
# # 适应市场波动性的动态止损：使用ATR来确定市场波动性，基于这个动态调整止损点。
# # 尾随止损（Trailing Stop）：当交易变得有利时，尾随止损可以帮助锁定盈利。
# # 动态仓位管理：根据市场波动性和账户的风险承受能力动态调整仓位大小。
# # 趋势过滤：仅在特定的趋势条件下交易，比如当SMA在上升趋势中交易。
# # 在这个策略中，我们结合了SMA、RSI和MACD指标来增加买卖点的精确性。MACD用于确认趋势的方向和强度，而RSI帮助识别过度买入或卖出的情况。这个策略同样应用了尾随止损，以便在趋势继续时保护利润。
# # 请注意，策略的最终表现强烈依赖于历史数据和参数的选择。每个市场和股票都有其特性，这就需要针对具体情况调整策略参数。
# # BASE LINE #1
# class OptimizedStrategy2(bt.Strategy):
#     params = {
#         'sma_period': 10,
#         'rsi_period': 14,
#         'atr_period': 14,
#         'macd_fast': 12,
#         'macd_slow': 26,
#         'macd_signal': 9,
#         'risk_per_trade': 0.01,
#         'trail_stop_atr': 2,
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SMA(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.macd = bt.indicators.MACD(
#             period_me1=self.params.macd_fast,
#             period_me2=self.params.macd_slow,
#             period_signal=self.params.macd_signal
#         )
#         self.crossover = bt.indicators.CrossOver(self.sma, self.data.close)
#
#     def next(self):
#         atr_value = self.atr[0]
#         if not self.position:
#             if self.crossover > 0 and self.rsi < 70 and self.macd > 0:
#                 size = (self.broker.get_cash() * self.params.risk_per_trade) / atr_value
#                 self.buy(size=size)
#
#         if self.position:
#             if self.crossover < 0 or self.rsi > 70 or self.macd < 0:
#                 self.sell(size=self.position.size)
#             else:
#                 # Dynamic trailing stop
#                 if self.data.close > self.position.price + atr_value * self.params.trail_stop_atr:
#                     self.sell(size=self.position.size, exectype=bt.Order.StopTrail, trailamount=atr_value)
#
# # 为了设计一个更激进的策略，我们可以考虑以下几点：
# #
# # 调整入市和出市策略：降低入市的RSI门槛，提高出市的RSI门槛，以更积极地把握买卖机会。
# # 引入多个时间框架：结合不同时间框架的SMA，以确定更强的买卖信号。
# # 盈利目标和止损：设置具体的盈利目标和止损点，以实现利润最大化和亏损控制。
# # 成交量过滤：仅在成交量高于平均水平时交易，以确保市场动力。
# # 价格行为分析：识别关键支撑/阻力位，结合技术分析进行买卖决策。
# # 此策略使用了更激进的RSI门槛值来判定入市和出市点，同时结合成交量和ATR来设定具体的盈利目标和止损。在实际应用此策略前，请进行详尽的历史数据测试，并调整参数以适应您的交易风格和风险偏好。
# class AggressiveStrategy(bt.Strategy):
#     params = {
#         'sma_period_short': 10,
#         'sma_period_long': 30,
#         'rsi_period': 14,
#         'rsi_entry': 50,  # 更激进的买入RSI阈值
#         'rsi_exit': 50,  # 更激进的卖出RSI阈值
#         'atr_period': 14,
#         'volume_period': 30,  # 成交量平均天数
#         'profit_target': 3,  # 盈利目标是ATR的倍数
#         'stop_loss': 2,  # 止损是ATR的倍数
#     }
#
#     def __init__(self):
#         self.sma_short = bt.indicators.SMA(period=self.params.sma_period_short)
#         self.sma_long = bt.indicators.SMA(period=self.params.sma_period_long)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.params.volume_period)
#
#     def next(self):
#         if not self.position:
#             if (self.data.close > self.sma_short and self.rsi > self.params.rsi_entry and
#                 self.data.volume > self.volume_ma):
#                 size = self.broker.get_cash() / self.data.close
#                 self.buy(size=size)
#                 self.sell(size=size, exectype=bt.Order.Limit,
#                           price=self.data.close[0] * (1 + self.params.profit_target / 100))
#                 self.sell(size=size, exectype=bt.Order.Stop,
#                           price=self.data.close[0] * (1 - self.params.stop_loss / 100))
#
#         if self.position and self.rsi < self.params.rsi_exit:
#             self.close()


# Considering the issues with the current strategy, let's focus on an approach that better captures trends and reversals. Here's an adjusted strategy that:
#
# Uses a combination of short and long SMA for trend detection and signal generation.
# Employs RSI to filter signals in overbought or oversold conditions, aiming for a balanced risk profile.
# Implements a trailing stop based on ATR to lock in profits during strong trends and limit losses during reversals.
# class BalancedTrendFollowingStrategy(bt.Strategy):
#     params = {
#         'short_sma': 10,
#         'long_sma': 30,
#         'rsi_period': 14,
#         'rsi_upper': 70,
#         'rsi_lower': 30,
#         'atr_period': 14,
#         'risk_per_trade': 0.02,
#         'trail_atr_multiple': 2,
#     }
#
#     def __init__(self):
#         self.short_sma = bt.indicators.SMA(period=self.params.short_sma)
#         self.long_sma = bt.indicators.SMA(period=self.params.long_sma)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#
#         # Trailing stop price
#         self.trail_stop_price = None
#
#     def next(self):
#         if self.position:
#             # Check if we need to update our trailing stop
#             if self.data.close > self.trail_stop_price:
#                 self.trail_stop_price = self.data.close - self.atr[0] * self.params.trail_atr_multiple
#
#             # Check if we need to sell
#             if self.data.close <= self.trail_stop_price or self.rsi > self.params.rsi_upper:
#                 self.close()  # Close the position
#                 self.trail_stop_price = None  # Reset trailing stop price
#
#         elif (self.short_sma > self.long_sma and
#               self.rsi < self.params.rsi_upper and
#               self.data.close > self.short_sma):
#
#             # Calculate the number of shares
#             shares = (self.broker.getcash() * self.params.risk_per_trade) / self.atr[0]
#             # Buy with all the cash available in the broker
#             self.buy(size=shares)
#
#             # Set the initial trailing stop price
#             self.trail_stop_price = self.data.close - self.atr[0] * self.params.trail_atr_multiple


# Use a combination of SMA indicators to gauge the overall trend.
# Employ the RSI to filter potential entry and exit points to avoid overbought or oversold conditions.
# Incorporate the MACD to confirm the trend's direction.
# Apply an ATR-based trailing stop to protect profits and limit losses.
# Include a volume filter to confirm the strength of the trend.
# This strategy uses several technical indicators to attempt to capture trends and exit before reversals. The ATR is used to set a dynamic risk level for each trade, and the profit target and trailing stop are based on a multiple of ATR to lock in profits.
# class ComplexStrategy(bt.Strategy):
#     params = {
#         'sma_fast': 10,
#         'sma_slow': 30,
#         'rsi_period': 14,
#         'macd_fast': 12,
#         'macd_slow': 26,
#         'macd_signal': 9,
#         'atr_period': 14,
#         'volume_ma_period': 20,
#         'risk_per_trade': 0.01,
#         'profit_factor': 3,
#         'trailing_stop_factor': 2,
#     }
#
#     def __init__(self):
#         self.sma_fast = bt.indicators.SMA(period=self.params.sma_fast)
#         self.sma_slow = bt.indicators.SMA(period=self.params.sma_slow)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         # Corrected MACD initialization
#         self.macd = bt.indicators.MACD(
#             period_me1=self.params.macd_fast,
#             period_me2=self.params.macd_slow,
#             period_signal=self.params.macd_signal
#         )
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.params.volume_ma_period)
#
#
#         # To keep track of pending orders and buy price/commission
#         self.order = None
#         self.buyprice = None
#         self.buycomm = None
#
#     def notify_order(self, order):
#         if order.status in [order.Submitted, order.Accepted]:
#             # Buy/Sell order submitted/accepted to/by broker - Nothing to do
#             return
#
#         if order.status in [order.Completed]:
#             if order.isbuy():
#                 self.buyprice = order.executed.price
#                 self.buycomm = order.executed.comm
#             self.order = None
#
#         elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#             self.order = None
#
#     def next(self):
#         if self.order:
#             return
#
#         if not self.position:
#             if self.data.close > self.sma_fast and self.rsi < 70 and self.macd > 0 and self.data.volume > self.volume_ma:
#                 # Buy based on the risk per trade and ATR value
#                 size = (self.broker.getcash() * self.params.risk_per_trade) / self.atr[0]
#                 self.order = self.buy(size=size)
#         else:
#             if self.data.close < self.sma_fast or self.rsi > 70 or self.macd < 0:
#                 self.order = self.sell(size=self.position.size)
#             elif self.data.close > self.buyprice * self.params.profit_factor:
#                 self.order = self.sell(size=self.position.size)
#             elif self.data.close < self.buyprice * (1 - (self.atr[0] * self.params.trailing_stop_factor)):
#                 self.order = self.sell(size=self.position.size)
#

# BASELINE #2
# class ResponsiveStrategy(bt.Strategy):
#     params = {
#         'sma_period': 50,  # Longer period for trend following
#         'rsi_period': 14,
#         'rsi_overbought': 70,
#         'rsi_oversold': 30,
#         'macd_fast': 12,
#         'macd_slow': 26,
#         'macd_signal': 9,
#         'atr_period': 14,
#         'risk_per_trade': 0.01,
#         'profit_target_factor': 3,  # Target profit as a factor of ATR
#         'stop_loss_factor': 2,  # Stop loss as a factor of ATR
#     }
#
#     def __init__(self):
#         self.sma = bt.indicators.SMA(period=self.params.sma_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.macd = bt.indicators.MACD(period_me1=self.params.macd_fast, period_me2=self.params.macd_slow,
#                                        period_signal=self.params.macd_signal)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#
#     def next(self):
#         cash = self.broker.get_cash()
#         atr_value = self.atr[0]
#         position_size = (cash * self.params.risk_per_trade) / atr_value
#
#         if not self.position:
#             # Buy logic - look for convergence of positive signals
#             if self.data.close > self.sma and self.rsi < self.params.rsi_overbought and self.macd > 0:
#                 self.buy(size=position_size)
#
#                 # Setting a profit target
#                 profit_target = self.data.close + (atr_value * self.params.profit_target_factor)
#                 self.sell(exectype=bt.Order.Limit, price=profit_target, size=position_size)
#
#                 # Setting a stop loss
#                 stop_loss = self.data.close - (atr_value * self.params.stop_loss_factor)
#                 self.sell(exectype=bt.Order.Stop, price=stop_loss, size=position_size)
#
#         else:
#             # Sell logic - look for divergence of negative signals
#             if self.data.close < self.sma or self.rsi > self.params.rsi_overbought or self.macd < 0:
#                 self.close()  # This will cancel profit target & stop loss orders as well

# BASELINE 3
# from backtrader.indicators import ExponentialMovingAverage as EMA
#
#
# class AdaptiveStrategy(bt.Strategy):
#     params = {
#         'fast_ema_period': 12,
#         'slow_ema_period': 26,
#         'signal_ema_period': 9,
#         'rsi_period': 14,
#         'atr_period': 14,
#         'rsi_upper': 70,
#         'rsi_lower': 30,
#         'risk_per_trade': 0.01,
#         'volatility_threshold': 0.02  # ATR percentage threshold to consider a stock volatile
#     }
#
#     def __init__(self):
#         self.fast_ema = EMA(period=self.params.fast_ema_period)
#         self.slow_ema = EMA(period=self.params.slow_ema_period)
#         self.signal_ema = EMA(period=self.params.signal_ema_period)
#         self.macd = self.fast_ema - self.slow_ema
#         self.macdsignal = EMA(self.macd, period=self.params.signal_ema_period)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#
#         self.in_trade = False
#
#     def next(self):
#         if not self.in_trade:
#             # Check if the stock is less volatile and has a strong trend
#             if (self.atr[0] / self.data.close[0] < self.params.volatility_threshold and
#                     self.macd[0] > self.macdsignal[0] and
#                     self.rsi[0] < self.params.rsi_upper):
#                 size = (self.broker.getcash() * self.params.risk_per_trade) / self.atr[0]
#                 self.buy(size=size)
#                 self.in_trade = True
#
#         else:
#             # Check if the trend is weakening or stock becomes more volatile
#             if (self.atr[0] / self.data.close[0] > self.params.volatility_threshold or
#                     self.macd[0] < self.macdsignal[0] or
#                     self.rsi[0] > self.params.rsi_upper):
#                 self.close()
#                 self.in_trade = False

# class AdaptiveStrategy(bt.Strategy):
#     params = {
#         'fast_ema': 12,
#         'slow_ema': 26,
#         'signal_ema': 9,
#         'rsi_period': 14,
#         'rsi_overbought': 70,
#         'rsi_oversold': 30,
#         'atr_period': 14,
#         'risk_per_trade': 0.01,
#         'volatility_threshold': 0.02,
#     }
#
#     def __init__(self):
#         # Indicators
#         self.ema_fast = bt.indicators.EMA(period=self.params.fast_ema)
#         self.ema_slow = bt.indicators.EMA(period=self.params.slow_ema)
#         self.macd = bt.indicators.MACD(self.data.close, period_me1=self.params.fast_ema,
#                                         period_me2=self.params.slow_ema,
#                                         period_signal=self.params.signal_ema)
#         self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
#         self.atr = bt.indicators.ATR(period=self.params.atr_period)
#         self.order = None
#
#     def log(self, txt, dt=None):
#         ''' Logging function for this strategy'''
#         dt = dt or self.datas[0].datetime.date(0)
#         print(f'{dt.isoformat()}, {txt}')  # Comment this out in live trading
#
#     def next(self):
#         if self.order:  # Check if an order is pending, if so, we cannot send a second order
#             return
#
#         if not self.position:  # Not in the market
#             if (self.macd[0] > self.macd.signal[0]) and (self.rsi < self.params.rsi_overbought):
#                 # A buy signal (MACD above signal and RSI not overbought)
#                 self.order = self.buy()
#                 self.log(f'BUY CREATE, {self.data.close[0]}')
#
#         else:  # In the market
#             if (self.macd[0] < self.macd.signal[0]) or (self.rsi > self.params.rsi_overbought):
#                 # A sell signal (MACD below signal or RSI is overbought)
#                 self.order = self.sell()
#                 self.log(f'SELL CREATE, {self.data.close[0]}')

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
