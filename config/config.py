# -------------------------------------------------------
# General config 
# -------------------------------------------------------

# Directory path for saving and loading datasets. 
DATASET_DIR = "dataset" 

# Define th starting and ending date when collecting the ticker data. 
TICKER_DATE_COLLECT = "1998-12-01", "2021-12-17" 

# Define the list of tickers we are interested to investigate on. 
TICKER_TO_COLLECT = [
	"XLF", "XHB", "XLK", "XLY", "XLP", 
	"XRT", "XLI", "XLB", "XTL", "XLU", 
	"XLE", 
] 

# Define the filename to collect the event dates. 
EVENTS_FILENAMES = [
	"observance_dates_ext.csv", 
	"firsttrdrday_ofmonth.csv", 
	"santa_rally.csv", 
	"triple_witching_week.csv", 
]

# Identify the list of keywords. We can add as many relevant keywords here as we want. 
NEWS_KEYWORDS_MAPPING = {
	"news_ffr": ["fed fund", "ffr"], 
	"news_fed": ["federal", "fed reserve", "federal reserve"], 
	"news_earnings": ["earnings", "earnings announcement", "earnings report"], 
	"news_interest_rate": ["interest rate"], 
	"news_rate_hikes": ['rate hikes'] 
}

METRICS_OPTIONS = [ 
	"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", "vix_chg_c2c", 
	"volume_diff_to_med", "volume_pchg_from_med", 
	"tscore_bo", "tscore_c2o", "tscore_o2c", "tscore_c2c", "vix_tscore_c2c", 
]

INTENT_MEASURES = {
	"dir": {
		"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
		"volume_pchg_from_med", 
	}, 
	"mag": {
		"price_chg_c2o", "price_chg_o2c", "price_chg_c2c", 
		"tscore_bo", "tscore_c2o", "tscore_o2c", "tscore_c2c", 
	}, 
	"avg": {
		"vix_chg_c2c", "vix_tscore_c2c", 
	}
} 

RE_PATS_AND_CONDITIONS = {
	"_dir_\\d": 0.7,
	"_mag_\\d": 0.9, 
	"_avg_\\d": 2.0, 
}
