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
		start_date:str=TICKER_DATE_COLLECT[0], 
		end_date:str=TICKER_DATE_COLLECT[1], 
		use_csv:bool=False, 
		file_name:str="sector_price_history_processed_stg_1.csv", 
	) -> None:

		# The primary dataframe for analysis. 
		if use_csv == False:
			print("Pulling Ticker data from Yahoo Finance")

			# An array of Ticker instances. 
			self.ticker_data = [GetTickerData(ticker_name, start_date, end_date) for ticker_name in ticker_names]

			# A dataframe resulting from unioning the history attribute of each Ticker instance 
			self.unioned_history = pd.concat([ticker.get_processed() for ticker in self.ticker_data]) 

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
		df_with_vix = df.merge(right=GetImpVolatility().get_processed(), how="left", left_on="date", right_on="date", validate="many_to_one") 
		return df_with_vix 
