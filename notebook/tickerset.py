
from ticker import *
from dataset import *
import pandas as pd 

class TickerSet(DataSet):
	'''A DatSet specific to a group of ticker symbols, fetches ticker data for a provided list
	   union all ticker history together, join with volatility measures, and provide time series statistics''' 
	def __init__(self, 
				ticker_names=["XLF", "XHB", "XLK", "XLY", "XLP", "XRT", "XLI", "XLB", "XTL", "XLU"], 
				use_csv=False, 
				file_name = "sector_price_history.csv") -> None:
		#The primary dataframe for analysis
		if use_csv == False:
			print("Pulling Ticker data from Yahoo Finance")
			#an array of Ticker instances
			self.ticker_data = [Ticker(ticker_name) for ticker_name in ticker_names]
			#a dataframe resulting from unioning the history attribute of each Ticker instance 
			self.unioned_history = pd.concat([ticker.history for ticker in self.ticker_data])
			#set default data frame
			self.df = self.get_df_with_vix()
		DataSet.__init__( self,file_name, use_csv)

	def get_df_with_vix(self):
		'''Joins the unioned ticker history data with Volatility ticker data '''
		#starts with all histories unioned
		df = self.unioned_history.reset_index(drop=False) 
		#lower cases all columns
		df.columns = [c.lower() for c in df.columns] 
		#join with an history from Volatility ticker
		df_with_vix = df.merge(right=Volatility().vix_history, how="left", left_on="date", right_on="Date", validate="many_to_one") 
		return df_with_vix

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
		df_tickers = self.df

		# 1. price_chg_close_to_open
		prev_close = df_tickers["close"].shift(1)
		df_tickers["price_chg_c2o"] = (df_tickers["open"] - prev_close) / prev_close 

		# 2. price_chg_open_to_close
		df_tickers["price_chg_o2c"] = (df_tickers["close"] - df_tickers["open"]) / df_tickers["open"] 

		# 3. price_chg_close_to_close
		df_tickers["price_chg_c2c"] = df_tickers["close"].pct_change(1) 

		return df_tickers

		
	def compute_rolling_volume(self, df):
		'''Compute the 3 months rolling median volume'''
		df_tickers = df
		cols = ["volume"] 
		df_tickers["volume_rollmed"] = df_tickers[cols].rolling(window=90, min_periods=90, win_type=None).median() 

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
		tp_rollavg = tp.rolling(window=360, min_periods=90, win_type=None).mean() 
		tp_rollstd = tp.rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 

		# Compute Bollinger Band. 
		n_std = 2 
		df_tickers["bo_upper"] = tp_rollavg + n_std * tp_rollstd 
		df_tickers["bo_lower"] = tp_rollavg - n_std * tp_rollstd 

		# Compute the z-score using closing price and Bollinger Band. 
		df_tickers["zscore_bo"] = (df_tickers["close"] - tp_rollavg) / tp_rollstd 

		# Compute the z-score for price change. 
		price_chg_c2o_rollavg = df_tickers["price_chg_c2o"].rolling(window=360, min_periods=90, win_type=None).mean() 
		price_chg_o2c_rollavg = df_tickers["price_chg_o2c"].rolling(window=360, min_periods=90, win_type=None).mean() 
		price_chg_c2c_rollavg = df_tickers["price_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).mean() 

		price_chg_c2o_rollstd = df_tickers["price_chg_c2o"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 
		price_chg_o2c_rollstd = df_tickers["price_chg_o2c"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 
		price_chg_c2c_rollstd = df_tickers["price_chg_c2c"].rolling(window=360, min_periods=90, win_type=None).std(ddof=0) 

		df_tickers["zscore_c2o"] = (df_tickers["price_chg_c2o"] - price_chg_c2o_rollavg) / price_chg_c2o_rollstd 
		df_tickers["zscore_o2c"] = (df_tickers["price_chg_o2c"] - price_chg_o2c_rollavg) / price_chg_o2c_rollstd 
		df_tickers["zscore_c2c"] = (df_tickers["price_chg_c2c"] - price_chg_c2c_rollavg) / price_chg_c2c_rollstd 

		return df_tickers 

