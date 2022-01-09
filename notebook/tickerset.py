
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
			self.unioned_history = pd.concat([ticker.get_processed() for ticker in self.ticker_data])
			#set default data frame
			self.df = self.get_df_with_vix()
		DataSet.__init__( self,file_name, use_csv)

	def get_df_with_vix(self):
		'''Joins the unioned ticker history data with Volatility ticker data '''
		#starts with all histories unioned
		df = self.unioned_history.reset_index(drop=False) 
	
		#join with an history from Volatility ticker
		df_with_vix = df.merge(right=Volatility().vix_history, how="left", left_on="Date", right_on="Date", validate="many_to_one") 
		return df_with_vix

	 

