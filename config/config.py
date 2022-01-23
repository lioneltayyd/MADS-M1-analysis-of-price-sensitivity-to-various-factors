# -------------------------------------------------------
# General config 
# -------------------------------------------------------

# Directory path for saving and loading datasets. 
DATASET_DIR = "dataset" 

# Define th starting and ending date when collecting the ticker data. 
TICKER_DATE_COLLECT = "2007-11-30", "2021-12-17" 

# Define the list of tickers we are interested to investigate on. 
TICKER_TO_COLLECT = [
	"XLF", "XHB", "XLK", "XLY", "XLP", 
	"XRT", "XLI", "XLB", "XLU", "XLE", 
] 

# Define the filename to collect the event dates. 
EVENTS_FILENAMES = [
	"observance_dates_ext.csv", 
	"santa_rally.csv", 
	"triple_witching_week.csv", 
	"economic_reported_date.csv",
	"news_headline_keywords.csv" 
]

# Identify the list of keywords. We can add as many relevant keywords here as we want. 
NEWS_KEYWORDS_MAPPING = {
	"news_ffr": ["fed fund", "ffr"], 
	"news_fed": ["federal", "fed reserve", "federal reserve"], 
	"news_earnings": ["earnings", "earnings announcement", "earnings report"], 
	"news_interest_rate": ["interest rate"], 
	"news_rate_hikes": ["rate hikes"] 
}

# Map the metrics to the intended processing step for analysis. 
# dir = Compute the probability of exceeding a specific threshold. 
# abv = Compute the probability of exceeeding above the specified threshold. 
# mag = Compute the magnitude. Ignore direction. 
# avg = Compute the average value. 
INTENT_MEASURES = {
	"dir": set([
		"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
	]), 
	"abv": set([
		"volume_pchg_from_med", 
	]), 
	"mag": set([
		"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", "vix_chg_c2c", 
		"tscore_c2o", "tscore_o2c", "tscore_c2c", "vix_tscore_c2c", 
	]), 
	"avg": set([

	]), 
} 

# Set the conditions or thresholds for each intended processing step (listed as keys value). 
# The following keys will be used as a regex pattern to process the data. 
RE_PATS_AND_CONDITIONS = {
	"_dir_\\d": 0.66, 
	"_abv_\\d": 0.66, 
	"_mag_\\d": 0.9, 
	"_avg_\\d": 0.5, 
}

# List oof metrics to identify convergence. 
METRICS_TO_IDENTIFY_CONVERGENCE = [
	"tscore_c2c_mag_1", "volume_pchg_from_med_abv_1", "vix_tscore_c2c_mag_1"
]

# List of metrics to explore with. 
METRIC_CHOICES = [ 
	"tscore_c2o_mag_1", "tscore_c2c_mag_1", "tscore_o2c_mag_1", "vix_tscore_c2c_mag_1", 
	"price_chg_c2o_dir_1", "price_chg_c2c_dir_1", "price_chg_o2c_dir_1", 
	"volume_pchg_from_med_abv_1", 
]

# Recession data. To be parsed into Pandas DataFrame. 
RECESSIONS = {
	"recession"	: ["Covid 2019", "DebtCrisis 2008", "DotCom 2001"], 
	"date_start": ["2020-02-01", "2007-11-01", "2001-03-01"], 
	"date_end"	: ["2020-04-01", "2009-06-01", "2001-11-01"], 
}
