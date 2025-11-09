from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
from pathlib import Path
import pandas as pd
from typing import (
	Optional,
	List,
	Final,
)
from enum import StrEnum
from RankingList import (
	dataset,
	filter,
	clean,
)
from RankingList.dataset import (
	UserRankingList
)
from RankingList.clean import (
	UserListClean,
)
from RankingList.filter import (
	UserListFilter,
	UserListPreFilter,
)
import time
import AnimeList.clean
from AnimeList.dataset import AnimeListColumns
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.CP2')
''' TODO
- [ ] Fetch dataset

- [ ] Clean
	- [ ] Remove invalid records
	- [ ] Fix invalid values, if we need to.

- [ ] Filter
	- [ ] ANIME_ID must be in our filtered & cleaned ANIME dataset.
	- [ ] 

- [ ] Boxplots for each feature
- [ ] Measure covariance of features
- [ ] Visualize covariant features
- [ ] UMAP, TSNE of data
'''

''' NOTE
 	My computer likely cannot handle loading this entire dataset at once.
	 	There are 80,076,112 records.
	We are going to ignore the following columns due to sparsity:
		- TAGS
		- REWATCHING
		- REWATCHING_EP
	We might ignore the following due to sparsity and lack of usability/reliability:
		- START_DATE
		- FINISH_DATE
		- LAST_UPDATED
	We primarily care about:
		- USERNAME
		- ANIME_ID
		- WATCHED_EPISODES
		- SCORE
		- STATUS
'''
class Stopwatch():
	''' class used to print time durations. '''
	start_time:float
	end_time:float
	def __init__(self):
		self.start_time=0
		self.end_time=0
	def start(self):
		self.start_time = time.time()
	def end(self):
		self.end_time = time.time()
	def __str__(self):
		seconds = self.end_time - self.start_time
		if seconds > 60:
			return f'{seconds:0.2f}s / {seconds/60:0.2f} minutes'
		else:
			return f'{seconds:0.2f}s'
def run():
	_logger.info('Begin.')
	SUBSET_NROWS:Final[int] = int(dataset.raw_dataset_length)
	_logger.info('Fetch raw user_rankings and the clean anime_list')
	user_rankings = dataset.UserRankingList(nrows=SUBSET_NROWS,usecols=dataset.columns_for_retrieval)
	anime_list = AnimeList.clean.AnimeListClean(usecols=[AnimeListColumns.ANIME_ID])

	# order of operations
	# - FILTER_1 (filters by anime_list)
	# - CLEAN_1 (removes invalid records)
	# - FILTER_2 (filters to what we want)
	sw = Stopwatch()

	# PRE FILTER - Remove records where the ANIME_ID is not found in our cleaned anime list
	_logger.info('Perform Prefiltering on raw data... (The removal of anime_id not found in our clean dataset).')	
	sw.start()
	pref,prefo = UserListPreFilter.from_rankings(
		raw_rankings=user_rankings, anime_list=anime_list
	)
	sw.end()
	_logger.info(f'Prefiltering(1) took: {str(sw)}')

	_logger.info('Perform cleaning on prefiltered data...')
	sw.start()
	clean, cleanedOut = UserListClean.from_filter(ranking=pref)
	sw.end()
	_logger.info(f'Cleaning(2) took: {str(sw)}')

	
	_logger.info('Perform filtering on cleaned data...')
	sw.start()
	filtered, filteredOut = UserListFilter.from_clean(cleaned_rankings=clean)
	sw.end()
	_logger.info(f'Filtering(3) took: {str(sw)}')

	# Print differecnes
	output:List[str] = [
		'Lengths of each list:',
		f'0\tRaw Rankings: {user_rankings.get_frame().shape[0]}'
		f'1\tPrefiltered: {pref.get_frame().shape[0]}'
		f'2\tCleaned: {clean.get_frame().shape[0]}'
		f'3\tFiltered: {filtered.get_frame().shape[0]}'
	]
	_logger.info('\n'.join(output))
	# ---
	_logger.info('End.')
	return