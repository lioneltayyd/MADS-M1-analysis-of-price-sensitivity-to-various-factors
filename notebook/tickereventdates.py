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

		# I have identified the dates for each event using Julia (programming language) 
		# previously and saved them in CSV. I own the Julia source code (belongs to me). 
		# It is extremely cumbersome to calculate the date pattern in Python. 
		# Inaccurate dates will occur starting from 2030. Plus, difficult to provide customised 
		# date pattern. I haven't discover another library that can do that conveniently. 

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



class ConsolidateDates(ManageDataset):
	'''ManageDataset specific to ticker time series data combined with event date data'''

	def __init__(self, use_csv=False, file_name="sector_price_history_processed_stg_2.csv"): 
		self.tickers = ProcessTickerData(use_csv=True)

		print("Loading Event Dates" )
		self.event_dates = GetEventDates() 

		print("Loading Economic Reporting Dates From CSV")
		self.ecomonic_reported_dates = ManageDataset("economic_reported_date.csv")

		print("Loading News Headlines From CSV") 
		self.news_headlines = ProcessNewsData() 

		if use_csv == False:
			print("Adding Event Flag columns to ticker history") 
			self.df = self.get_df_with_date_flags() 

		ManageDataset.__init__(self, file_name, use_csv) 


	def add_event_flags(self, df_tickers, df_event_dates):
		'''Adds boolean as integer columns for each event according to matching rows in ticker data.'''

		for event_name in df_event_dates.columns: 
			# Default to 0. 
			if event_name not in df_tickers.columns: 
				df_tickers[event_name] = 0 
			
			# Filter non economic report dates and assign 1. 
			boo_dates = df_tickers["date"].isin(df_event_dates[event_name].values) 
			df_tickers.loc[boo_dates, event_name] = 1 

		return df_tickers 

	
	def add_news_flags(self, df_tickers:pd.DataFrame, df_news:pd.DataFrame, headline_keywords:pd.DataFrame): 
		'''Adds boolean as integer columns for each headline keyword according to matching rows in ticker data.'''

		self.news_headline_keywords = set()

		for col in headline_keywords.columns: 
			# Merge (headline_keywords) series with the (df_news) dataframe. 
			df_reported_dates = df_news.merge(right=headline_keywords[col], how="left", left_index=True, right_index=True) 

			# Convert into long table. 
			df_reported_dates = df_reported_dates \
				.pivot(columns=col, values="date").iloc[:, 1:] \
				.dropna(how="all") 

			# Store unique headline keywords. 
			self.news_headline_keywords.update(df_reported_dates.columns.to_list())  

			# Add a flag for each news reporting date. 
			df_tickers = self.add_event_flags(df_tickers, df_reported_dates) 

		# Convert set into list object to make it convenient to concat with other list object. 
		self.news_headline_keywords = list(self.news_headline_keywords) 

		return df_tickers 


	def get_df_with_date_flags(self):
		'''Runs processing steps to add event flags to ticker data for each of the two event datas.'''

		df_consolidated_dates = self.add_event_flags(self.tickers.df, self.event_dates.df) 
		df_consolidated_dates = self.add_event_flags(df_consolidated_dates, self.ecomonic_reported_dates.df) 
		df_consolidated_dates = self.add_news_flags(df_consolidated_dates, self.news_headlines.df, self.news_headlines.headline_keywords) 
		return df_consolidated_dates
