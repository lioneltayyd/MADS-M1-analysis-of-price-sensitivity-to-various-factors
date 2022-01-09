# %%
# Python modules. 
import pandas as pd
import yfinance as yf

# Custom configuration.
from config.config import TICKER_DATE_COLLECT



# %%
# Define a Ticker class for fetching and storing data from yahoo finance ticker api. 
class GetTickerData():
	'''Fetches and stores data for a Ticker from Yahoo Finance Ticker API'''

	def __init__(self, ticker_name:str, start_date:str=TICKER_DATE_COLLECT[0], end_date:str=TICKER_DATE_COLLECT[1]) -> None:
		self.name = ticker_name
		self.start_date = start_date
		self.end_date = end_date

		print("Creating yf Ticker instance for " + self.name + ", fetching history")
		
		self.ticker = yf.Ticker(self.name) 


	def get_processed(self):
		'''Runs the processing functions for applying additional time series statistics.'''

		ticker_data = self.get_history() 
		processed_data = self.compute_price_change(ticker_data) 
		processed_data = self.compute_rolling_volume(processed_data) 
		processed_data = self.compute_bollinger(processed_data) 
		processed_data = self.compute_price_chg_tscore(processed_data) 
		processed_data = self.compute_vix_chg_tscore(processed_data) 

		return processed_data


	def get_history(self):
		try:
			history = self.ticker.history(period="max", interval="1d", start=self.start_date, end=self.end_date, auto_adjust=True, rounding=True) 
			history["ticker"] = self.name 
			history.columns = [c.lower() for c in history.columns] 
		except:
			print("Data not available from yahoo finance")
		return history 


	def compute_price_change(self, df:pd.DataFrame):
		'''	
		We will be computing 3 types of price difference. 2nd option is not a must but just 
		want to compare the difference between open and closing market. 

		1. Gapping / Close market price change. Difference between previous day 
		   closing price and current day open price. 
		2. Open market price change. Difference between current day open and closing price. 
		3. Daily price change. Difference between previous day and current day closing price.
		'''

		# 1. price_chg_close_to_open
		prev_close = df["close"].shift(1) 
		df["price_chg_c2o"] = (df["open"] - prev_close) / prev_close 

		# 2. price_chg_open_to_close
		df["price_chg_o2c"] = (df["close"] - df["open"]) / df["open"] 

		# 3. price_chg_close_to_close
		df["price_chg_c2c"] = df["close"].pct_change(1) 

		return df

		
	def compute_rolling_volume(self, df:pd.DataFrame):
		'''
		Compute the 3 months rolling median volume and the volume difference to the rolling median. 
		'''

		cols = ["volume"] 
		df["volume_rollmed"] = df[cols].rolling(window=90, min_periods=90, win_type=None).median() 

		# Compute the difference between each volume with the 3 months rolling median volume. 
		df["volume_diff_to_med"] = df["volume"] - df["volume_rollmed"] 

		# Compute the percent change from the 3 months rolling median volume. Comparing 
		# percent change between each period is easier than looking at the difference. 
		df["volume_pchg_from_med"] = df["volume_diff_to_med"] / df["volume_rollmed"] 

		return df

	
	def compute_bollinger(self, df:pd.DataFrame):
		'''
		Compute Bollinger Band and Bollinger tscore to measure price change magnitude. 
		'''

		# Refer to this link to understand what Bollinger Band is and its formula. 
		# https://www.investopedia.com/terms/b/bollingerbands.asp

		# We will use 360 days for the rolling window. If the window is too short, 
		# the average price could fluctuate higher or lower. We can't use median 
		# because we need to calculate t-score. 

		# Compute the rolling average and standard deviation. 
		tp =  (df["close"] + df["low"] + df["high"]) / 3 
		tp_rollavg = tp.rolling(window=360, min_periods=360, win_type=None).mean() 
		tp_rollstd = tp.rolling(window=360, min_periods=360, win_type=None).std(ddof=0) 


		# Compute Bollinger Band. 
		n_std = 2 
		df["bo_upper"] = tp_rollavg + (n_std * tp_rollstd) 
		df["bo_lower"] = tp_rollavg - (n_std * tp_rollstd) 

		# Compute the z-score using closing price and Bollinger Band. 
		df["tscore_bo"] = (df["close"] - tp_rollavg) / tp_rollstd 

		return df 


	def compute_price_chg_tscore(self, df:pd.DataFrame): 
		'''Compute tscore to measure price change magnitude.'''

		# Compute the t-score for price change. 
		price_chg_c2o_rollavg = df["price_chg_c2o"].rolling(window=360, min_periods=360, win_type=None).mean() 
		price_chg_o2c_rollavg = df["price_chg_o2c"].rolling(window=360, min_periods=360, win_type=None).mean() 
		price_chg_c2c_rollavg = df["price_chg_c2c"].rolling(window=360, min_periods=360, win_type=None).mean() 

		price_chg_c2o_rollstd = df["price_chg_c2o"].rolling(window=360, min_periods=360, win_type=None).std(ddof=0) 
		price_chg_o2c_rollstd = df["price_chg_o2c"].rolling(window=360, min_periods=360, win_type=None).std(ddof=0) 
		price_chg_c2c_rollstd = df["price_chg_c2c"].rolling(window=360, min_periods=360, win_type=None).std(ddof=0) 

		df["tscore_c2o"] = (df["price_chg_c2o"] - price_chg_c2o_rollavg) / price_chg_c2o_rollstd 
		df["tscore_o2c"] = (df["price_chg_o2c"] - price_chg_o2c_rollavg) / price_chg_o2c_rollstd 
		df["tscore_c2c"] = (df["price_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 

		return df 


	def compute_vix_chg_tscore(self, df:pd.DataFrame): 
		'''Compute tscore to measure price change magnitude.'''

		# Compute the t-score for VIX. 
		price_chg_c2c_rollavg = df["vix_chg_c2c"].rolling(window=360, min_periods=360, win_type=None).mean() 

		price_chg_c2c_rollstd = df["vix_chg_c2c"].rolling(window=360, min_periods=360, win_type=None).std(ddof=0) 

		df["vix_tscore_c2c"] = (df["vix_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 

		return df 



# %%
class GetImpVolatility(GetTickerData):
	'''Extends Ticker with modifications specific to the Implied Volatility Index'''

	def __init__(self): 
		GetTickerData.__init__(self, ticker_name="^VIX") 
		self.vix_history = self.get_vix_history() 


	def get_vix_history(self): 
		'''Renames open and close measures and adds new measures for distance from threshold''' 

		base_columns = ["open", "close"] 
		renamed_columns = [f"vix_{column}".lower() for column in base_columns] 

		# Filter and rename columns. 
		vix = self.get_history()[base_columns] 
		vix.columns = renamed_columns 

		# Convert index name to lowercase. 
		vix.index.name = vix.index.name.lower() 

		# Compute VIX change between the previous and current day close. 
		vix.loc[:, "vix_chg_c2c"] = vix["vix_close"].pct_change(1) 

		return vix
