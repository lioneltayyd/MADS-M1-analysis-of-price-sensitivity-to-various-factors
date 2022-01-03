import yfinance as yf

#Define a Ticker class for fetching and storing data from yahoo finance ticker api 
class Ticker():
	'''Fetches and stores data for a Ticker from Yahoo Finance Ticker API'''
	def __init__(self,ticker_name: str, 
				start_date="1998-12-01", 
				end_date="2021-12-17") -> None:
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

class Volatility(Ticker):
	'''Extends Ticker with modifications specific to the Volatility Index '''
	def __init__(self):
		Ticker.__init__(self, ticker_name = "^VIX")
		self.vix_history = self.get_vix_history()
		return
	def get_vix_history(self):
		'''Renames open and close measures and adds new measures for distance from threshold ''' 
		base_columns = ["Open", "Close"]
		renamed_columns = [f"vix_{column}".lower() for column in base_columns] 

		vix = self.history[base_columns] 
		vix.columns = renamed_columns
		# Minus the open, high, low, close with the threshold. If the value 
		# exceeds the threshold, that means traders assume the future price 
		# movement could be more volatile. Vice versa. VIX is also known as 
		# a fear indicator. 
		vix_threshold = 18
		for c in vix.columns: 
			#vix[f"{c}_minus_thresh"] = vix[c] - vix_threshold
			vix.loc[:,(f"{c}_minus_thresh")] = vix[c] - vix_threshold
		return vix