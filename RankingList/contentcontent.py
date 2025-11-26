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
from scipy.sparse import csr_matrix
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.RankingList.ContentContent')
import umap

class UserContentScore():
	''' A sparse matrix of user-content scores '''
	matrix:csr_matrix
	username_codes:pd.Categorical
	item_codes:pd.Categorical
	default_path:Final[Path] = Path('content-by-content.csv')
	def __init__(self, filter:UserListFilter) -> None:
		frame = filter.get_frame()[[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE]].dropna().copy()
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

	def get_matrix(self):
		return self.matrix
	
	def run_umap(self):
		reducer = umap.UMAP()
		data=self.get_matrix()
		_logger.info('Plotting UMAP...')
		embedding = reducer.fit_transform(data)
		return pd.DataFrame(embedding, columns=['UMAP-X','UMAP-Y'])
