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

	score_min:int
	score_max:int
	frac:float # The fraction of the dataset loaded.
	
	folder:Path
	name:str
	file_dataset:Path
	file_frame:Path

	def get_name(self):
		return f'UCS score_{self.score_min}_{self.score_max} frac_{self.frac}'

	@staticmethod
	def filter_frame_by_score(filter:UserListFilter, score_min:int, score_max:int)->pd.DataFrame:
		'''Fraction is of the already filtered(score [lte,gte]) frame.'''
		filter_frame = filter.get_frame()
		og_rows = filter_frame.shape[0]
		_logger.debug(f'min:{score_min} max:{score_max}')
		_logger.debug(f'get_frame_sample original shape: {og_rows}')

		mask_score_range = (
			(filter_frame[UserRankingColumn.SCORE] >= score_min)
			& (filter_frame[UserRankingColumn.SCORE] <= score_max)
		)
		filter_frame.drop(filter_frame.loc[~mask_score_range].index,inplace=True)
		new_rows = filter_frame.shape[0]
		if new_rows == 0: raise RuntimeError('no rows')
		_logger.debug(f'Removed {og_rows-new_rows} records which do not match score filter.')
		
		og_rows=filter_frame.shape[0]
		frame = filter_frame[[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE]].dropna().drop_duplicates().copy()
		# .sample(frac=frac,axis='index')
		new_rows=frame.shape[0]
		_logger.info(f'Score sample shape {frame.shape}')
		return frame

	def __init__(self, filter:UserListFilter,
			  score_min:int, score_max:int,
			  frac:float, parent_folder:Path) -> None:
		'''
		parent_folder: the folder above the folder which will contains this data.
			- e.g., parent_folder='foobar' we will store data in foobar/$NAME
		'''
		sw = stopwatch.Stopwatch()
		# 0. save args
		self.score_max = score_max
		self.score_min = score_min
		self.frac = frac
		# 1. mkdir RUN_ID
		self.name = self.get_name()
		self.folder = parent_folder.joinpath(self.name)
		self.folder.mkdir(mode=0o775, exist_ok=True,parents=True)
		self.file_dataset = self.folder.joinpath('dataset.npz')
		self.file_frame = self.folder.joinpath('frame.csv')
		file_anime_codes = self.folder.joinpath('item_codes.pkl')
		file_username_codes = self.folder.joinpath('username_codes.pkl')
		file_sampled_index =  self.folder.joinpath('sampld_index.pkl')
		# 2. if Dataset.npz exists, load & stop.
		if self.file_dataset.exists():
			_logger.info(f'Loading {self.file_dataset}')
			self.data_matrix = load_npz(self.file_dataset)

			# TODO check if these files exist. If not load the filter_frame & regenerate them.
			with open(file_username_codes,'rb') as f:
				self.username_codes = pickle.load(f)
			with open(file_anime_codes,'rb') as f:
				self.item_codes = pickle.load(f)
		# 3. else process data and save.
		else:
			frame = UserContentScore.get_frame_sample(filter=filter, frac=self.frac, score_min=score_max, score_max=score_min)

			sw.start()
			# Reencode Usernames
			self.username_codes = pd.Categorical(frame[UserRankingColumn.USERNAME])
			file_username_codes.unlink(missing_ok=True)
			with open(file_username_codes,'wb') as f:
				pickle.dump(self.username_codes,f)
			# Reencode Anime
			self.item_codes = pd.Categorical(frame[UserRankingColumn.ANIME_ID])
			file_anime_codes.unlink(missing_ok=True)
			with open(file_anime_codes,'wb') as f:
				pickle.dump(self.item_codes, f)
			# Copy to frame for ease of use later.
			frame[UserRankingColumn.ANIME_ID + '_code'] = self.item_codes.codes
			frame[UserRankingColumn.USERNAME + '_code'] = self.username_codes.codes
			sw.end()
			_logger.debug(f'saving categorical data took: {str(sw)}')
			# Create the csr matrix
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
			_logger.debug(f'Generating {self.name} matrix took: {str(sw)}')
			self.save_matrix_data()
			sw.start()
			frame.to_csv(self.file_frame,index_label='INDEX')
			sw.end()
			_logger.debug(f'Saving frame took: {str(sw)}')

	def get_matrix(self):
		return self.data_matrix
	
	def save_matrix_data(self):
		sw = stopwatch.Stopwatch()
		sw.start()
		save_npz(file=self.file_dataset, matrix=self.get_matrix())
		sw.end()
		_logger.debug(f'Saving matrix took: {str(sw)}')
	
	def run_umap(self, n_neighbors:int, min_dist:float,metric:str, do_plot:bool)->pd.DataFrame:
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
			_logger.info(f'Applying UMAP {label}')
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
			_logger.debug('saving umap to file')
			sw.start()
			umap_data.to_csv(file_data,index=False)
			sw.end()
			_logger.debug(f'saving to csv took: {str(sw)}')
		
		if do_plot and ((not file_plot.exists()) or new_data):
			sw.start()
			_logger.info('Plotting umap')
			f,ax = plt.subplots()
			sns.scatterplot(ax=ax,
				x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
				data=umap_data, legend='auto',alpha=0.5,
				palette=sns.color_palette("mako", as_cmap=True)
			)
			f.set_size_inches(10,10)
			f.set_dpi(500)
			sw.end()
			_logger.debug(f'creating graph took: {str(sw)}')
			sw.start()
			f.savefig(file_plot)
			sw.end()
			_logger.debug(f'saving graph took: {str(sw)}')
			plt.close(fig=f)
		else:
			_logger.info('skipping. no need to plot.')
		return umap_data