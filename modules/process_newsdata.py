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
	def __init__(self, use_csv:bool=False, filename:str="news_headline_keywords.csv") -> None:
		
		self.topic_keywords = NEWS_KEYWORDS_MAPPING
		self.topics = list(self.topic_keywords.keys())

		if use_csv == False:
			self.articles = ManageDataset("raw_partner_headlines.csv").df
			print("Transferring to EventsDate Format")
			self.df = self.get_event_dates()

		ManageDataset.__init__(self, filename, use_csv)


	def get_event_dates(self):
		matching_headlines = {
			topic: self.get_dates(self.topic_keywords[topic], self.articles) for topic in self.topics 
		}

		df_headline_keywords = pd.concat(
			list(matching_headlines.values()),
			keys=list(matching_headlines.keys()),
			axis=1
		)
		return df_headline_keywords


	def get_dates(self, keywords:dict, df:pd.DataFrame):
		match_indicator = self.get_key_word_match_indicator(keywords, df)
		matches = match_indicator[match_indicator == True]
		dates = pd.concat([matches, df["date"]], axis=1, join="inner")["date"].str[:-9]
		return dates


	def get_key_word_match_indicator(self, keywords:dict, df:pd.DataFrame):
		# Combine the keywords into a regex pattern.
		re_pattern = f"""({"|".join(keywords)})"""

		# Extract matches. 
		matches = df.loc[:, "headline"].str.findall(re_pattern, flags=re.IGNORECASE) 

		match_indicator = matches.str.len() > 0
		return match_indicator
