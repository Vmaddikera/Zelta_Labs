# region imports
from AlgorithmImports import *
# endregion

class Regime(QCAlgorithm):


    def initialize(self) -> None:
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2023, 12, 1)
        # Set the brokerage and account type for accurate fee and margin behavior.
        self.set_brokerage_model(BrokerageName.BINANCE, AccountType.CASH)
        # In some Crypto brokerages, USD is not a valid currency to trade.
        # Therefore, set the account currency to USDT and add the starting cash.
        self.set_account_currency("USDT", 10000)
        # Subscribe to the Crypto pairs.
        # You don't need to specify the market because the Binance brokerage model already does that.
        self.btc = self.add_crypto("BTCUSDT", market=Market.BINANCE)
        self.eth = self.add_crypto("ETHUSDT", market=Market.BINANCE)
        # Create the indicators.
        self._btc.frama = self.frama(self._qqq.symbol, 16)
        self._btc.rsi = RelativeStrengthIndex(10)
        










        





        # Create a 5-minute consolidator to aggregate AAPL tick data into quote bars.
        consolidator = TickQuoteBarConsolidator(timedelta(minutes=5))
        # Subscribe the consolidator for automatic updates.
        self.subscription_manager.add_consolidator(self._aapl.symbol, consolidator)
        # Attach an event handler handler to update the RSI indicator with the consolidated bars.
        consolidator.data_consolidated += lambda _, bar: self._aapl.rsi.update(bar.end_time, bar.close)
        # Warm up the indicators.
        self.warm_up_indicator(self._qqq.symbol, self._qqq.frama)
        for quote_bar in self.history[QuoteBar](self._aapl.symbol, 10, Resolution.MINUTE):
            self._aapl.rsi.update(quote_bar.end_time, quote_bar.close)