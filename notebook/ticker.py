import yfinance as yf
import numpy as np

#Define a Ticker class for fetching and storing data from yahoo finance ticker api 
class Ticker():
	'''Fetches and stores data for a Ticker from Yahoo Finance Ticker API'''
	def __init__(self,ticker_name: str, 
				start_date="1998-12-01", 
				end_date="2021-12-17") -> None:
		self.name = ticker_name
		self.start_date = start_date
		self.end_date = end_date
		print("Creating yf Ticker instance for " + self.name + ", fetching history")
		self.ticker = yf.Ticker(self.name)

	def get_history(self):
		try:
			history = self.ticker.history(period="max", interval="1d", start=self.start_date, end=self.end_date, auto_adjust=True, rounding=True) 
			history["ticker"] = self.name
			history.columns = [c.lower() for c in history.columns] 
		except:
			print("Data not available from yahoo finance")
		return history 

	def get_processed(self):
		'''Runs the processing functions for applying additional time seires statistics'''
		price_change = self.compute_price_change() 
		rolling_volume = self.compute_rolling_volume(price_change)
		bollinger_and_z = self.compute_bollinger_and_z_score(rolling_volume)
		return bollinger_and_z

	def compute_price_change(self):
		'''	# We will be computing 3 types of price difference. 2nd option is not a must but just 
		# want to compare the difference between open and closing market. 

		# 1. Gapping / Close market price change. Difference between previous day 
		# 	 closing price and current day open price. 
		# 2. Open market price change. Difference between current day open and closing price. 
		# 3. Daily price change. Difference between previous day and current day closing price.'''
		df_tickers = self.get_history()

		# 1. price_chg_close_to_open
		df_tickers['prev_close'] = df_tickers["close"].shift(1)
		#As first row's prev_close will be Nan, the best substitute is the current close
		df_tickers.loc[np.isnan(df_tickers.prev_close), ['prev_close']] =df_tickers.loc[np.isnan(df_tickers.prev_close), ['close']]['close'] 

		df_tickers["price_chg_c2o"] = (df_tickers["open"] - df_tickers['prev_close']) / df_tickers['prev_close'] 

		# 2. price_chg_open_to_close
		df_tickers["price_chg_o2c"] = (df_tickers["close"] - df_tickers["open"]) / df_tickers["open"] 

		# 3. price_chg_close_to_close
		df_tickers["price_chg_c2c"] = df_tickers["close"].pct_change(1) 

		return df_tickers

		
	def compute_rolling_volume(self, df):
		'''Compute the 3 months rolling median volume'''
		df_tickers = df
		cols = ["volume"] 
		df_tickers["volume_rollmed"] = df_tickers[cols].rolling(window=90, min_periods=1).median() 

		# Compute the difference between each volume with the 3 months rolling median volume. 
		df_tickers["volume_diff_to_med"] = df_tickers["volume"] - df_tickers["volume_rollmed"] 

		# Compute the percent change from the 3 months rolling median volume. Comparing 
		# percent change between each period is easier than looking at the difference. 
		df_tickers["volume_pchg_from_med"] = df_tickers["volume_diff_to_med"] / df_tickers["volume_rollmed"] 
		return df_tickers

	
	def compute_bollinger_and_z_score(self, df):
		df_tickers = df
		# Refer to this link to understand what Bollinger Band is and its formula. 
		# https://www.investopedia.com/terms/b/bollingerbands.asp

		# We will use 360 days for the rolling window. If the window is too short, 
		# the average price could fluctuate higher or lower. We can't use median 
		# because we need to calculate t-score. 

		# Compute the rolling average and standard deviation. 
		tp =  (df_tickers["close"] + df_tickers["low"] + df_tickers["high"]) / 3 
		tp_rollavg = tp.rolling(window=360, min_periods=1).mean() 
		tp_rollstd = tp.rolling(window=360, min_periods=1).std(ddof=0).fillna(0) 

		# Compute Bollinger Band. 
		n_std = 2 
		df_tickers["bo_upper"] = tp_rollavg + n_std * tp_rollstd 
		df_tickers["bo_lower"] = tp_rollavg - n_std * tp_rollstd 

		# Compute the z-score using closing price and Bollinger Band. 
		df_tickers["zscore_bo"] = (df_tickers["close"] - tp_rollavg) / tp_rollstd 

		# Compute the z-score for price change. 
		price_chg_c2o_rollavg = df_tickers["price_chg_c2o"].rolling(window=360, min_periods=1).mean() 
		price_chg_o2c_rollavg = df_tickers["price_chg_o2c"].rolling(window=360, min_periods=1).mean() 
		price_chg_c2c_rollavg = df_tickers["price_chg_c2c"].rolling(window=360, min_periods=1).mean() 

		price_chg_c2o_rollstd = df_tickers["price_chg_c2o"].rolling(window=360, min_periods=1).std(ddof=0).fillna(0)
		price_chg_o2c_rollstd = df_tickers["price_chg_o2c"].rolling(window=360, min_periods=1).std(ddof=0).fillna(0)
		price_chg_c2c_rollstd = df_tickers["price_chg_c2c"].rolling(window=360, min_periods=1).std(ddof=0).fillna(0)

		df_tickers["zscore_c2o"] = (df_tickers["price_chg_c2o"] - price_chg_c2o_rollavg) / price_chg_c2o_rollstd 
		df_tickers["zscore_o2c"] = (df_tickers["price_chg_o2c"] - price_chg_o2c_rollavg) / price_chg_o2c_rollstd 
		df_tickers["zscore_c2c"] = (df_tickers["price_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 
        #From above
		return df_tickers.replace([np.inf, -np.inf], 0).fillna(0)

class Volatility(Ticker):
	'''Extends Ticker with modifications specific to the Volatility Index '''
	def __init__(self):
		Ticker.__init__(self, ticker_name = "^VIX")
		self.vix_history = self.get_vix_history()
		return
	def get_vix_history(self):
		'''Renames open and close measures and adds new measures for distance from threshold ''' 
		base_columns = ["open", "close"]
		renamed_columns = [f"vix_{column}".lower() for column in base_columns] 

		vix = self.get_history()[base_columns] 
		vix.columns = renamed_columns
		# Minus the open, high, low, close with the threshold. If the value 
		# exceeds the threshold, that means traders assume the future price 
		# movement could be more volatile. Vice versa. VIX is also known as 
		# a fear indicator. 
		vix_threshold = 18
		for c in vix.columns: 
			#vix[f"{c}_minus_thresh"] = vix[c] - vix_threshold
			vix.loc[:,(f"{c}_minus_thresh")] = vix[c] - vix_threshold
		return vix