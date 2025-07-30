# Create an EMA indicator for trade signal generation.
        self._ema = self.ema(self._future, 20, Resolution.DAILY)
        # Warm up the indicator for immediate readiness to trade with.
        self.warm_up_indicator(self._future, self._ema, Resolution.DAILY)

# Create a 252-day EMA indicator as a trend estimator.
        self._future.ema = self.ema(self._future.symbol, 252, Resolution.DAILY)


class CountConsolidatorAlgorithm(QCAlgorithm):
    # Create EMA indicators for trade signal generation.
    _ema = ExponentialMovingAverage(14)
    # The _day variable controls trade daily when open.
    _day = -1
    def initialize(self) -> None:
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2022, 2, 1)
        
        # Request SPY data to feed to indicators and trade.
        self.spy = self.add_equity("SPY", Resolution.TICK).symbol
        # Create a 10000 trade tick consolidator to feed the "volume" bar to the EMA indicator for trend entry/exit signal.
        tick_consolidator = TickConsolidator(10000)
        # Subscribe the consolidators to SPY data to automatically update the indicators.
        self.register_indicator(self.spy, self._ema, tick_consolidator)
        self.set_warm_up(120)
    def on_data(self, slice: Slice) -> None:
        ticks = slice.ticks.get(self.spy)
        if self._ema.is_ready and ticks and self._day != slice.time.day:
            # Obtain the latest quote price from the latest tick.
            last_tick = sorted(ticks, key=lambda x: x.end_time, reverse=True)[0]
            ema = self._ema.current.value
            # Trade the trend by EMA crosses.
            if last_tick.price > ema and not self.portfolio[self.spy].is_long:
                self.set_holdings(self.spy, 0.5)
            elif last_tick.price < ema and not self.portfolio[self.spy].is_short:
                self.set_holdings(self.spy, -0.5)
            self._day = slice.time.day


class HurstExponentAlgorithm(QCAlgorithm):
    def initialize(self) -> None:
        self._symbol = self.add_equity("SPY", Resolution.DAILY).symbol
        self.window_size = 100
        self.prices = []

    def on_data(self, slice: Slice) -> None:
        bar = slice.bars.get(self._symbol)
        if not bar:
            return

        # Store closing prices
        self.prices.append(bar.Close)

        # Keep only the last 'window_size' prices
        if len(self.prices) > self.window_size:
            self.prices.pop(0)

        # Compute Hurst Exponent when we have enough data
        if len(self.prices) == self.window_size:
            self.hurst = self.calculate_hurst(np.array(self.prices))

    def calculate_hurst(self, time_series):
        """Calculates the Hurst exponent using the R/S method."""
        N = len(time_series)
        T = np.arange(1, N + 1)
        Y = np.cumsum(time_series - np.mean(time_series))
        R = np.max(Y) - np.min(Y)
        S = np.std(time_series)

        # Avoid division by zero
        if S == 0:
            return 0.5  

        return np.log(R / S) / np.log(N)
