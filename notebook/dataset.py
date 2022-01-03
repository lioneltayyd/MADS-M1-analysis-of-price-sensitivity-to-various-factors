
import os
import pandas as pd

class DataSet():
	'''General dataset class with common methods needed for all data sets '''
	def __init__(self,file_name=None, use_csv=True, dataset_dir= 'dataset'):
		self.file_name = file_name
		self.dataset_dir=dataset_dir
		if use_csv:
			self.df = self.read_from_csv()
		self.column_list = self.df.columns.tolist()
	def write_to_csv(self):
		'''Write dataframe to csv file'''
		self.get_ready_for_file_operation()
		# Save the dataframe into CSV. 
		filepath = os.path.join(self.dataset_dir, self.file_name) 
		self.df.to_csv(filepath, index=False) 
	def read_from_csv(self):
		'''Read csv file into dataframe '''
		self.get_ready_for_file_operation()
		# Read the csv to a dataframe
		print("Read from csv") 
		filepath = os.path.join(self.dataset_dir, self.file_name) 
		df = pd.read_csv(filepath)
		return df
	def get_ready_for_file_operation(self):
		'''Handles the necessary checks pior to any file operation'''
		self.confirm_current_working_directory()
		self.confirm_dataset_directory()
		return 
	def confirm_current_working_directory(self):
		'''Set working directory to project directory'''
		if os.getcwd()[-8:] == 'notebook':
			os.chdir("..")
	def confirm_dataset_directory(self):
		'''checks for existince of dataset directory and creates if needed'''
		if not os.path.exists(self.dataset_dir):
			os.makedirs(self.dataset_dir)






		
