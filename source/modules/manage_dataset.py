# %%
# Python modules. 
import os, re 
import pandas as pd

# Custom configuration.
from config.config import DATASET_DIR



# %%
class ManageDataset():
	'''General dataset class with common methods needed for all data sets '''

	def __init__(self, filename:str=None, use_csv:bool=True, dataset_dir:str=DATASET_DIR):
		self.filename = filename
		self.dataset_dir = dataset_dir

		if use_csv:
			self.df = self.read_from_csv() 
		self.column_list = self.df.columns.tolist() 


	def write_to_csv(self):
		'''Write dataframe to csv file'''

		print(f"Write to ({self.filename})") 

		self.get_ready_for_file_operation()
		filepath = os.path.join(self.dataset_dir, self.filename) 
		self.df.to_csv(filepath, index=False) 


	def read_from_csv(self):
		'''Read csv file into dataframe '''

		print(f"Read from ({self.filename})") 

		self.get_ready_for_file_operation()
		filepath = os.path.join(self.dataset_dir, self.filename) 
		df = pd.read_csv(filepath)
		return df


	def get_ready_for_file_operation(self):
		'''Handles the necessary checks pior to any file operation'''

		self.confirm_current_working_directory()
		self.confirm_dataset_directory() 


	def confirm_current_working_directory(self):
		'''Set working directory to project directory'''

		if re.match(r".+/notebook", os.getcwd()): 
			os.chdir("../..") 


	def confirm_dataset_directory(self):
		'''checks for existince of dataset directory and creates if needed'''

		if not os.path.exists(self.dataset_dir):
			os.makedirs(self.dataset_dir)
