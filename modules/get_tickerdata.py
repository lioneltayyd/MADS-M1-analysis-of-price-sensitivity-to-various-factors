# %%
# Python modules. 
import yfinance as yf

# Custom configuration.
from config.config import TICKER_DATE_COLLECT



# %%
# Define a Ticker class for fetching and storing data from yahoo finance ticker api. 
class GetTickerData():
	'''Fetches and stores data for a Ticker from Yahoo Finance Ticker API'''

	def __init__(self, ticker_name:str, start_date:str=TICKER_DATE_COLLECT[0], end_date:str=TICKER_DATE_COLLECT[1]) -> None:
		self.name = ticker_name
		self.start_date = start_date
		self.end_date = end_date

		print("Creating yf Ticker instance for " + self.name + ", fetching history")
		
		self.ticker = yf.Ticker(self.name) 
		self.history = self.get_history() 


	def get_history(self):
		try:
			history = self.ticker.history(period="max", interval="1d", start=self.start_date, end=self.end_date, auto_adjust=True, rounding=True) 
			history["ticker"] = self.name
		except:
			print("Data not available from yahoo finance")
		return history 



# %%
class GetImpVolatility(GetTickerData):
	'''Extends Ticker with modifications specific to the Implied Volatility Index'''

	def __init__(self): 
		GetTickerData.__init__(self, ticker_name="^VIX") 
		self.vix_history = self.get_vix_history() 


	def get_vix_history(self): 
		'''Renames open and close measures and adds new measures for distance from threshold''' 

		base_columns = ["Open", "Close"] 
		renamed_columns = [f"vix_{column}".lower() for column in base_columns] 

		# Filter and rename columns. 
		vix = self.history[base_columns] 
		vix.columns = renamed_columns 

		# Compute VIX change between the previous and current day close. 
		vix.loc[:, "vix_chg_c2c"] = vix["vix_close"].pct_change(1) 

		return vix
