# %%
# Python modules. 
import pandas as pd 

# Custom modules. 
from modules.get_tickerdata import * 
from modules.manage_dataset import * 

# Custom configuration.
from config.config import TICKER_TO_COLLECT



# %%
class ProcessTickerData(ManageDataset): 
	'''
	A DatSet specific to a group of ticker symbols, fetches ticker data for a provided list
	union all ticker history together, join with volatility measures, and provide time series statistics
	''' 

	def __init__(
		self, 
		ticker_names:list=TICKER_TO_COLLECT, 
		use_csv:bool=False, 
		file_name:str="sector_price_history_processed_stg_1.csv"
	) -> None:

		# The primary dataframe for analysis. 
		if use_csv == False:
			print("Pulling Ticker data from Yahoo Finance")

			# An array of Ticker instances. 
			self.ticker_data = [GetTickerData(ticker_name) for ticker_name in ticker_names]

			# A dataframe resulting from unioning the history attribute of each Ticker instance 
			self.unioned_history = pd.concat([ticker.history for ticker in self.ticker_data])

			# Merge the unioned ticker data with VIX data and set it as the default dataframe. 
			self.df = self.get_df_with_vix() 

		ManageDataset.__init__(self, file_name, use_csv) 


	def get_df_with_vix(self):
		'''Joins the unioned ticker history data with Volatility ticker data '''

		# Starts with all histories unioned. 
		df = self.unioned_history.reset_index(drop=False) 

		# Lower cases all columns. 
		df.columns = [c.lower() for c in df.columns] 
		
		# Join with an history from Implied Volatility Index ticker. 
		df_with_vix = df.merge(right=GetImpVolatility().vix_history, how="left", left_on="date", right_on="Date", validate="many_to_one") 
		return df_with_vix 


	def get_processed(self):
		'''Runs the processing functions for applying additional time series statistics.'''

		processed_data = self.compute_price_change(self.df) 
		processed_data = self.compute_rolling_volume(processed_data) 
		processed_data = self.compute_bollinger(processed_data) 
		processed_data = self.compute_price_chg_tscore(processed_data) 
		processed_data = self.compute_vix_chg_tscore(processed_data) 

		return processed_data


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
		tp_rollavg = tp.rolling(window=360, min_periods=90, win_type=None).mean() 
		tp_rollstd = tp.rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 


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
		price_chg_c2o_rollavg = df["price_chg_c2o"].rolling(window=360, min_periods=90, win_type=None).mean() 
		price_chg_o2c_rollavg = df["price_chg_o2c"].rolling(window=360, min_periods=90, win_type=None).mean() 
		price_chg_c2c_rollavg = df["price_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).mean() 

		price_chg_c2o_rollstd = df["price_chg_c2o"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 
		price_chg_o2c_rollstd = df["price_chg_o2c"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 
		price_chg_c2c_rollstd = df["price_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 

		df["tscore_c2o"] = (df["price_chg_c2o"] - price_chg_c2o_rollavg) / price_chg_c2o_rollstd 
		df["tscore_o2c"] = (df["price_chg_o2c"] - price_chg_o2c_rollavg) / price_chg_o2c_rollstd 
		df["tscore_c2c"] = (df["price_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 

		return df 


	def compute_vix_chg_tscore(self, df:pd.DataFrame): 
		'''Compute tscore to measure price change magnitude.'''

		# Compute the t-score for VIX. 
		price_chg_c2c_rollavg = df["vix_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).mean() 

		price_chg_c2c_rollstd = df["vix_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 

		df["vix_tscore_c2c"] = (df["vix_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 

		return df 
