from tickereventdates import *
import pandas as pd 
import numpy as np 
import re


class AggregateMeasures(DataSet):
	'''DataSet which creates and stores aggregate analysis of tickers and related events'''
	def __init__(self, 
				metric_options= [
					"vix_open_minus_thresh", "vix_close_minus_thresh", 
					"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
					"volume_diff_to_med", "volume_pchg_from_med", 
					"zscore_bo", "zscore_c2o", "zscore_o2c", "zscore_c2c", 
				], 
				dict_intent_measure = {
					"dir": {
						"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
						"volume_pchg_from_med", 
					}, 
					"mag": {
						"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
						"zscore_bo", "zscore_c2o", "zscore_o2c", "zscore_c2c", 
					},  
					"avg": {
						"vix_open_minus_thresh", "vix_close_minus_thresh", 
					}, 
				},
				use_csv=True, 
				file_name="sector_metrics_aggregate.csv",
				ticker_event_dates = None):
		
		if ticker_event_dates == None:
			self.ticker_event_dates = TickerEventDates()
		else:
			self.ticker_event_dates = ticker_event_dates

		self.factors = self.ticker_event_dates.event_dates.column_list + self.ticker_event_dates.ecomonic_reported_dates.column_list

		if use_csv == False:
			print("Creating aggregations")
			self.df = self.get_aggregation(metric_options, dict_intent_measure)
		DataSet.__init__(self, file_name, use_csv)
	def get_aggregation(self, metric_options, dict_intent_measure):
		df_tickers =  self.ticker_event_dates.df
		# An empty dataframe to consolidate all the aggregates for 
		# different metrics. 
		df_consolidated_agg = pd.DataFrame() 

		# To store the ticker and factor values. 
		arr_tickers, arr_factors = [], [] 

		# Start consolidating the aggregates. This will take a while. 
		for intent_measure, metrics in dict_intent_measure.items(): 

			# Define what we want to measure. 
			for metric in metrics: 

				# Define whether to measure the event or non-occuring event period. 
				for measure_event_period in [0, 1]: 

					# Define the variable to assign as the pivot value. 
					pivot_value = metric

					# Define the aggregate function. 
					aggfunc = np.mean

					# Define the name for the aggregated value. 
					aggvalue_name = metric

					# Define the positive threshold for probability count. 
					prob_threshold = 0  

					# An empty dataframe to consolidate all the pivot tables. 
					df_aggregates = pd.DataFrame() 

					# Consolidate all the pivot tables. 
					for factor in self.factors: 
						# Remove event or non-occuring event period (either 1 or 0) for that factor. 
						df_processed = df_tickers.loc[df_tickers[factor] == measure_event_period, :] 

						# Convert all negative to positive unless we are looking to measure 
						# the directional probability or distance from the threshold. 
						if intent_measure == "mag": 
							df_processed.loc[:, pivot_value] = df_processed.loc[:, pivot_value].abs() 

						# To compute directional probabilities, we need to conver the negatives to 0 
						# and positives to 1 before aggregating it with the mean. 
						if intent_measure == "dir": 
							df_processed.loc[df_processed[pivot_value] <= prob_threshold, pivot_value] = 0 
							df_processed.loc[df_processed[pivot_value] >  prob_threshold, pivot_value] = 1 

						# Convert to pivot table. Average the value across entire the timeframe. 
						df_pivottable = df_processed.pivot_table(values=pivot_value, index="ticker", columns=factor, aggfunc=aggfunc) 

						# Rename the column heading. 
						df_pivottable.columns.name = "factor" 

						# Rename the column. There should be only 1 colume in this case. 
						# The original column name will either be 0 or 1. 
						try: 
							df_pivottable.columns = [factor] 
						except:
							print("Failed on Metric: " + metric + " Factor: " + factor)

						# Combine all the pivot tables into a single dataframe. 
						df_aggregates = pd.concat([df_aggregates, df_pivottable], axis="columns") 

					# Convert into long table. 
					df_aggregates = df_aggregates \
						.reset_index(drop=False) \
						.melt(id_vars="ticker", var_name="factor", value_vars=df_aggregates.columns, value_name=aggvalue_name) 

					# Rename the metric name. Example (zscore_c2c) will be (zscore_c2c_mag) or 
					# (price_chg_c2o) will be (price_chg_c2o_dir). 
					metric_newname = f"{metric}_{intent_measure}_{measure_event_period}" 
					df_aggregates = df_aggregates.rename(mapper={metric: metric_newname}, axis="columns") 

					# Combine all the pivot tables into a single dataframe. 
					df_consolidated_agg = pd.concat([df_consolidated_agg, df_aggregates[[metric_newname]]], axis="columns") 

					if not arr_tickers and not arr_factors: 
						arr_tickers = df_aggregates["ticker"].to_list() 
						arr_factors = df_aggregates["factor"].to_list() 

				if intent_measure == "mag": 
					# Compute the value difference between occurring event and non-occuring event. 
					df_consolidated_agg[f"{metric}_{intent_measure}_diff"] = \
						df_consolidated_agg[f"{metric}_{intent_measure}_1"] - df_consolidated_agg[f"{metric}_{intent_measure}_0"] 

				# For clearing the warning output. The warning is not important. 
				#clear_output() 

		# Add new columns for tickers and factors. 
		df_consolidated_agg["ticker"] = arr_tickers 
		df_consolidated_agg["factor"] = arr_factors 

		# Rearragne the columns. 
		cols = ["ticker", "factor"] + df_consolidated_agg.columns[:-2].to_list() 
		df_consolidated_agg = df_consolidated_agg[cols]
		return df_consolidated_agg
	def identify_covergence(self,regex_pats_n_conditions = {"_dir_\\d" : 0.7,"_mag_\\d" : 0.9, "_avg_\\d" : 2.0 }):
		# Process on the copy instead of the original dataframe. 
		df_identify_convergence = self.df.copy() 
		# Gather matched column names. 
		cols = ["ticker", "factor"] 

		# Identify convergence. If all the required conditions for 
		# specific metrics are fulfilled, we will assume convergence. 
		for regex_pat, condition in regex_pats_n_conditions.items(): 
			# Get the columns that matches the regex. 
			cols_matched = [c for c in df_identify_convergence.columns if re.match(f"\\w+{regex_pat}", c)] 
			cols.extend(cols_matched) 

			for c in cols_matched: 
				if regex_pat in ["_mag_\\d", "_avg_\\d"]: 
					df_identify_convergence.loc[df_identify_convergence[c] <  condition, c] = 0 
					df_identify_convergence.loc[df_identify_convergence[c] >= condition, c] = 1 

				elif regex_pat == "_dir_\\d": 
					boo_neutral = (df_identify_convergence[c] >= (1 - condition)) & (df_identify_convergence[c] <= condition)
					df_identify_convergence.loc[boo_neutral, c] = 0 
					df_identify_convergence.loc[df_identify_convergence[c] <= (1 - condition), c] = 1 
					df_identify_convergence.loc[df_identify_convergence[c] >= condition, c] = 1 

		# Filter columns. 
		df_identify_convergence = df_identify_convergence[cols] 

		return df_identify_convergence