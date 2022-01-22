# %%
# Python modules. 
import pandas as pd 

# Custom modules. 
from modules.manage_dataset import * 
from modules.process_tickerdata import *
from modules.process_newsdata import * 

# Custom configuration.
from config.config import EVENTS_FILENAMES



# %%
class GetEventDates(ManageDataset):
	'''
	A ManageDataset specific to holding dates of observances and events. 
	Leverages Lionel's custom data CSVs which have a column per event and rows as dates of each event. 
	'''
	def __init__(self): 
		self.df = self.read_from_csv() 
		self.column_list = self.df.columns.to_list() 

	
	def read_from_csv(self):
		'''Overwrites default Dataset read opeartion to pull in the set of event data csvs'''

		df_event_dates = pd.DataFrame() 

		# Read the data and consolidate all the event dates. 
		for filename in EVENTS_FILENAMES: 
			# Read the data. 
			dates_df = ManageDataset(filename).df 

			# Sort the dates. Just to ensure it's in order. 
			event_dates = dates_df.sort_values(by=dates_df.columns.to_list())

			# Concat the dataframe. 
			df_event_dates = pd.concat([df_event_dates, event_dates], axis="columns") 
			
		return df_event_dates 



# %%
class ConsolidateDates(ManageDataset):
	'''ManageDataset specific to ticker time series data combined with event date data'''

	def __init__(self, use_csv=False, file_name="sector_price_history_processed_stg_2.csv"): 
		self.tickers = ProcessTickerData(use_csv=True)

		print("Loading Event Dates" )
		self.event_dates = GetEventDates() 

		if use_csv == False:
			print("Adding Event Flag columns to ticker history") 
			self.df = self.get_df_with_date_flags() 

		ManageDataset.__init__(self, file_name, use_csv) 


	def get_df_with_date_flags(self):
		'''Runs processing steps to add event flags to ticker data for each of the two event datas.'''
		df_consolidated_dates = self.add_event_flags(self.tickers.df, self.event_dates.df) 
		return df_consolidated_dates


	def add_event_flags(self, df_tickers:pd.DataFrame, df_event_dates:pd.DataFrame):
		'''Adds boolean as integer columns for each event according to matching rows in ticker data.'''

		for event_name in df_event_dates.columns: 
			# Default to 0. 
			if event_name not in df_tickers.columns: 
				df_tickers[event_name] = 0 
			
			# Filter non economic report dates and assign 1. 
			boo_dates = df_tickers["date"].isin(df_event_dates[event_name].values) 
			df_tickers.loc[boo_dates, event_name] = 1 

		return df_tickers 
