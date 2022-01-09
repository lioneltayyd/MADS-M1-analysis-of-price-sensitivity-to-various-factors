# %%
# Python modules. 
import pandas as pd 

# Custom modules. 
from modules.manage_dataset import * 
from modules.process_tickerdata import *

# Custom configuration.
from config.config import NEWS_KEYWORDS_MAPPING



# %%
class ProcessNewsData(ManageDataset):
	'''
	A ManageDataset specific to holding dates of observances and events. 
	Leverages Lionel's custom data CSVs which have a column per event and rows as dates of each event. 
	'''

	def __init__(self, use_csv:bool=False, file_name:str="news_headline_keywords.csv") -> None: 
		self.df = ManageDataset("raw_partner_headlines.csv").df 
		self.headline_keywords = self.get_processed() 

	
	def get_processed(self):
		'''Runs the processing functions.'''

		processed_data = self.process_dates(self.df) 
		processed_data = self.extract_keywords(processed_data) 

		return processed_data 


	def process_dates(self, df_news:pd.DataFrame): 
		# Remove the time part since we can't manipulate or do anything with it. 
		# Example: (2020-06-01 00:00:00) to (2020-06-01). 
		df_news["date"] = df_news["date"].str[:-9] 
		return df_news


	def extract_keywords(self, df_news:pd.DataFrame, keyword_mapping:dict=NEWS_KEYWORDS_MAPPING): 
		headline_keywords = [t for _, terms in keyword_mapping.items() for t in terms] 

		# Combine the keywords into a regex pattern. 
		re_pattern = f"""({"|".join(headline_keywords)})""" 

		# Extract the keywords based the regex patterns and indicate the occurance with binary value. 
		headline_keywords = df_news.loc[:, "headline"].str.findall(re_pattern, flags=re.IGNORECASE) 

		# Split the list of elements into multiple columns. 
		headline_keywords = pd.DataFrame(headline_keywords.to_list()) 

		# Lowercase the str. 
		headline_keywords = headline_keywords.apply(lambda x: x.str.lower(), axis=0) 

		# Map similar keywords into a single keyword. Example (FFR) and (Fed Fund) share 
		# the same meaning, hence (Fed Fund) should be converted to (FFR) and counted as 
		# a single keyword to avoid duplicates. 
		keyword_mapping = {t: k for k, terms in keyword_mapping.items() for t in terms} 
		headline_keywords = headline_keywords.apply(lambda x: x.map(keyword_mapping, na_action="ignore"), axis=0) 

		return headline_keywords
