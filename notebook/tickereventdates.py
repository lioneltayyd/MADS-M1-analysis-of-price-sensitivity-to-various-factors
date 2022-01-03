from dataset import *
from tickerset import *
import pandas as pd

class EventDates(DataSet):
	'''A DataSet specific to holding dates of events. 
	Leverages Lionel's custom data CSVs which have a column per event and rows as dates of each event'''
	def read_from_csv(self):
		'''Overwrites default Dataset read opeartion to pull in the set of event data csvs'''
		# I have identified the dates for each event using Julia (programming language) 
		# previously and saved them in CSV. I own the Julia source code (belongs to me). 
		# It is extremely cumbersome to calculate the date pattern in Python. 
		# Refer to "Mark The Dates For Each Event ((With Python)" section in this notebook. 
		# Inaccurate dates will occur starting from 2030. Plus, difficult to provide customised 
		# date pattern. I haven't discover another library that can do that conveniently. 
		filenames = ["event_dates_ext.csv", "firsttrdrday_ofmonth.csv", "santa_rally.csv", "triple_witching_week.csv"] 
		dfs = []
		# Read the data and consolidate all the event dates. 
		for filename in filenames: 
			# Read the data.
			dates_df = DataSet(filename).df
			# Sort the dates. Just to ensure it's in order. 
			event_dates = dates_df.sort_values(by=dates_df.columns.to_list())

			dfs.append(event_dates)
		return pd.concat(dfs, axis="columns")


class TickerEventDates(DataSet):
	'''DataSet specific to ticker time series data combined with event date data'''
	def __init__(self, 
				use_csv=False, 
				file_name="sector_price_history_processed_stg_1.csv"):
		self.tickers = TickerSet(use_csv=True)
		print("Loading Event Dates" )
		self.event_dates = EventDates()
		print("Loading Economic Reporting Dates From CSV" )
		self.ecomonic_reported_dates = DataSet("economic_reported_date.csv")
		if use_csv == False:
			print("Adding Event Flag columns to ticker history")
			self.df = self.get_df_with_date_flags()#.copy()
		DataSet.__init__(self, file_name, use_csv)

	def add_event_flags(self, df_tickers, df_event_dates):
		'''Adds boolean as integer columns for each event according to matching rows in ticker data'''
		for event_name in df_event_dates.columns: 
			# Default to 0. 
			df_tickers[event_name] = 0 
			# Filter non economic report dates and assign 1. 
			boo_dates = df_tickers["date"].isin(df_event_dates[event_name].values) 
			df_tickers.loc[boo_dates, event_name] = 1 
		return df_tickers

	def get_df_with_date_flags(self):
		'''Runs processing steps to add event flags to ticker data for each of the two event datas '''
		df_event_dates = self.add_event_flags(self.tickers.get_processed(), self.event_dates.df)
		df_all_dates = self.add_event_flags(df_event_dates, self.ecomonic_reported_dates.df)
		return df_all_dates