import matplotlib.pyplot as plt
from helpers.stopwatch import Stopwatch
import seaborn as sns
from dataset.dataset import DatasetCSV

from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
from helpers.stopwatch import Stopwatch
from pathlib import Path
import pickle
import pandas as pd
from typing import (
	Optional,
	List,
	Tuple,
	Final,
)
from RankingList.dataset import (
	UserRankingList,
	UserRankingColumn,
	StatusEnum,
	ranking_list_raw_len,
	columns_for_retrieval as ranking_list_columns_for_retrieval,
	UserListPreFilter,
	UserListPreFilterOut,
	UserListClean,
	UserListCleanOut,
	UserListFilter,
	UserListFilterOut,
)

from AnimeList.clean import AnimeListClean
from AnimeList.dataset import AnimeListColumns
import logging as _logging
from scipy.sparse import csr_matrix, save_npz, load_npz
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.RankingList.ContentContent')
import umap
import numpy as np
import pickle
from helpers import stopwatch

class UserContentScore():
	''' A sparse matrix of user-content scores '''
	data_matrix:csr_matrix
	username_codes:pd.Categorical
	item_codes:pd.Categorical

	is_binary:bool
	score_threshold:int
	frac:float # The fraction of the dataset loaded.
	drop_below_threshold:bool
	
	folder:Path
	name:str
	file_dataset:Path
	file_frame:Path

	def get_name(self):
		return f'UCS score_{self.score_threshold} frac_{self.frac} bin_{self.is_binary} drop_{self.drop_below_threshold}'

	@staticmethod
	def get_frame_sample(filter:UserListFilter, frac:float)->pd.DataFrame:
		filter_frame = filter.get_frame()
		og = filter_frame.shape
		_logger.debug(f'get_frame_sample original shape: {og}')
		frame = filter_frame[[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE]].dropna().sample(frac=frac,axis='index').copy()
		new = frame.shape
		_logger.info(f'get_frame_sample reduced by {og[0]-new[0]} rows. Rows:{new[0]}')
		return frame

	def __init__(self, filter:UserListFilter, binary:bool,
			  score_threshold_gt:int, drop_below_threshold:bool,
			  frac:float, parent_folder:Path) -> None:
		'''
		parent_folder: the folder above the folder which will contains this data.
			- e.g., parent_folder='foobar' we will store data in foobar/$NAME
		
		'''
		sw = stopwatch.Stopwatch()
		# 0. save args
		self.score_threshold = score_threshold_gt
		self.drop_below_threshold = drop_below_threshold
		self.frac = frac
		self.is_binary = binary
		# 1. mkdir RUN_ID
		self.name = self.get_name()
		self.folder = parent_folder.joinpath(self.name)
		self.folder.mkdir(mode=0o775, exist_ok=True,parents=True)
		self.file_dataset = self.folder.joinpath('dataset.npz')
		self.file_frame = self.folder.joinpath('frame.csv')
		file_anime_codes = self.folder.joinpath('item_codes.csv')
		file_username_codes = self.folder.joinpath('username_codes.csv')
		# 2. if Dataset.npz exists, load & stop.
		if self.file_dataset.exists():
			_logger.info(f'Loading {self.file_dataset}')
			self.data_matrix = load_npz(self.file_dataset)
			with open(file_username_codes,'rb') as f:
				self.username_codes = pickle.load(f)
			with open(file_anime_codes,'rb') as f:
				self.item_codes = pickle.load(f)
		# 3. else process data and save.
		else:
			sw.start()
			frame = UserContentScore.get_frame_sample(filter, self.frac)
			series_above_fiter = (frame[UserRankingColumn.SCORE] > score_threshold_gt)
			if self.is_binary:
				_logger.debug('binary data')
				frame['TEMP_BINARY'] = 0
				frame.loc[series_above_fiter, ['TEMP_BINARY']] = 1
				frame.drop(columns=[UserRankingColumn.SCORE], inplace=True)
				frame.rename(columns={'TEMP_BINARY':UserRankingColumn.SCORE},inplace=True)
			else: # Set all values not meeting threshold to 0 & then subtract values that did by the threshold.
				_logger.debug('non-binary data')
				frame.loc[~series_above_fiter, [UserRankingColumn.SCORE]]=0 # Values which did not reach threshold are 0.
				frame.loc[series_above_fiter,[UserRankingColumn.SCORE]]-=score_threshold_gt # Shift values
			if self.drop_below_threshold:
				_logger.debug('drop below theshold')
				frame.drop(index=frame.loc[~series_above_fiter].index, inplace=True)
			sw.end()
			_logger.debug(f'shape after processing: {frame.shape}. STOPWATCH: {str(sw)}')

			sw.start()
			self.username_codes = pd.Categorical(frame[UserRankingColumn.USERNAME])
			file_username_codes.unlink(missing_ok=True)
			with open(file_username_codes,'wb') as f:
				pickle.dump(self.username_codes,f)
			
			self.item_codes = pd.Categorical(frame[UserRankingColumn.ANIME_ID])
			file_anime_codes.unlink(missing_ok=True)
			with open(file_anime_codes,'wb') as f:
				pickle.dump(self.item_codes, f)
			sw.end()
			_logger.debug(f'saving categorical data took: {str(sw)}')
			frame[UserRankingColumn.ANIME_ID + '_code'] = self.item_codes.codes
			frame[UserRankingColumn.USERNAME + '_code'] = self.username_codes.codes
			sw.start()
			self.data_matrix = csr_matrix(
				(frame[UserRankingColumn.SCORE], # A 1-D array of values
					(
						self.username_codes.codes, # Same length as the score col. Indicates what row the value belongs to. ROW/indices
		  				self.item_codes.codes		# same len as score col. indicates what col the value belongs to.		COL/indptr
					)
				),
				shape=(len(self.username_codes.categories), len(self.item_codes.categories))
			)
			sw.end()
			_logger.info(f'Generating {self.name} matrix took: {str(sw)}')
			sw.start()
			self.save_matrix_data()
			sw.end()
			_logger.info(f'Saving matrix took: {str(sw)}')
			sw.start()
			frame.to_csv(self.file_frame,index_label='INDEX')
			sw.end()
			_logger.info(f'Saving frame took: {str(sw)}')

	def get_matrix(self):
		return self.data_matrix
	
	def save_matrix_data(self):
		save_npz(file=self.file_dataset, matrix=self.get_matrix())
	
	def run_umap(self, n_neighbors:int, min_dist:float,metric:str):
		''' Generate and plot umap data (if it doesnt exist already)'''
		label:str = f'm_{metric} n_{n_neighbors} d_{min_dist}'
		file_data = self.folder.joinpath(f'umap {label}.csv')
		file_plot = self.folder.joinpath(f'umap {label}.tiff')
		new_data:bool=False # Used to regenerate graph if it existed but the data had to be redone.
		sw = stopwatch.Stopwatch()
		if file_data.exists():
			_logger.info(f'loading umap data from: {file_data}')
			umap_data = pd.read_csv(file_data)
		else:
			new_data=True
			_logger.info(f'Plotting UMAP {label}')
			reducer = umap.UMAP(
				n_neighbors=n_neighbors,
				min_dist=min_dist,
				metric=metric
			)
			sw.start()
			embedding = reducer.fit_transform(self.get_matrix())
			sw.end()
			_logger.info(f'umap fit_transform took: {str(sw)}')
			umap_data = pd.DataFrame(embedding, columns=['UMAP-X','UMAP-Y'])
			_logger.info('saving umap to file')
			sw.start()
			umap_data.to_csv(file_data,index=False)
			sw.end()
			_logger.info(f'saving to csv took: {str(sw)}')
		
		if (not file_plot.exists()) or new_data:
			sw.start()
			_logger.info('Graphing umap')
			f,ax = plt.subplots()
			sns.scatterplot(ax=ax,
				x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
				data=umap_data, legend='auto',alpha=0.5,
				palette=sns.color_palette("mako", as_cmap=True)
			)
			f.set_size_inches(10,10)
			f.set_dpi(500)
			sw.end()
			_logger.info(f'creating graph took: {str(sw)}')
			sw.start()
			f.savefig(file_plot)
			sw.end()
			_logger.info(f'saving graph took: {str(sw)}')
			plt.close(fig=f)
		else:
			_logger.info('skipping. no need to plot.')
		return