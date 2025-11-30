from helpers.stopwatch import Stopwatch
from dataset.dataset import DatasetCSV

from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
from helpers.stopwatch import Stopwatch
from pathlib import Path
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

class UserContentScore():
	''' A sparse matrix of user-content scores '''
	matrix:csr_matrix
	username_codes:pd.Categorical
	item_codes:pd.Categorical
	binary:bool
	score_threshold:int
	default_path:Final[Path] = Path('content-by-content.csv')
	base_filename:Path
	def __init__(self, filter:UserListFilter, binary:bool, score_threshold_gt:int) -> None:
		self.binary = binary
		self.score_threshold = score_threshold_gt
		self.base_filename = Path(f'UCS st_{self.score_threshold} {'binary' if self.binary else 'non-binary'}') # TYPO! should have been UCS
		if self.base_filename.exists():
			_logger.info('Loading UCS from file')
			self.matrix = load_npz(self.base_filename)
		else:
			filter_frame = filter.get_frame()
			_logger.info(f'oriinal filter frame shape: {filter_frame.shape}')
			frame = filter_frame[[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE]].dropna().sample(frac=0.1,axis='index').copy()
			_logger.info(f'Binary? {binary}, score_filter={score_threshold_gt}')
			series_above_fiter = (frame[UserRankingColumn.SCORE] > score_threshold_gt)
			if binary: # Make the values true & false
				frame['TEMP_BINARY'] = False
				frame.loc[series_above_fiter, ['TEMP_BINARY']] = True
				frame.drop(columns=[UserRankingColumn.SCORE], inplace=True)
				frame.rename(columns={'TEMP_BINARY':UserRankingColumn.SCORE},inplace=True)
				_logger.info(frame.info())
			else: # Set all values not meeting threshold to 0 & then subtract values that did by the threshold.
				frame.loc[~series_above_fiter, [UserRankingColumn.SCORE]]=0 # Values which did not reach threshold are 0.
				frame.loc[series_above_fiter,[UserRankingColumn.SCORE]]-=score_threshold_gt # Shift values
				
			_logger.info(f'after sampling frame shape: {frame.shape}')
			sw = Stopwatch()
			self.username_codes = pd.Categorical(frame[UserRankingColumn.USERNAME])
			self.item_codes = pd.Categorical(frame[UserRankingColumn.ANIME_ID])
			sw.start()
			self.matrix = csr_matrix(
				(frame[UserRankingColumn.SCORE],
					(self.username_codes.codes, self.item_codes.codes)
				),
				shape=(len(self.username_codes.categories), len(self.item_codes.codes))
			)
			sw.end()
			_logger.info(f'Generating content collaboration matrix took {str(sw)}')
			self.save_matrix_data()
			frame.to_csv(f'{self.base_filename}.csv',index_label='INDEX')

	def get_matrix(self):
		return self.matrix
	
	def save_matrix_data(self):
		save_npz(file=f'{self.base_filename}.npz', matrix=self.get_matrix())
		self.username_codes
	
	def run_umap(self, label:str, **kwargs):
		reducer = umap.UMAP(**kwargs)
		data=self.get_matrix()
		_logger.info('Plotting UMAP...')
		embedding = reducer.fit_transform(data)
		umap_data = pd.DataFrame(embedding, columns=['UMAP-X','UMAP-Y'])
		umap_data.to_csv(f'{self.base_filename}_{label}_umap.csv')
		return umap_data
