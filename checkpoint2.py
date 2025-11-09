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
	Tuple,
	Final,
)
from RankingList.dataset import (
	UserRankingList,
	UserRankingColumn,
	StatusEnum,
	ranking_list_raw_len,
	columns_for_retrieval as ranking_list_columns_for_retrieval
)
from RankingList.prefilter import (
	UserListPreFilter,
	UserListPreFilterOut,
)
from RankingList.clean import (
	UserListClean,
	UserListCleanOut,
)
from RankingList.filter import (
	UserListFilter,
	UserListFilterOut,
)
import time
from AnimeList.clean import AnimeListClean
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


def prefilter_rankings(
		raw_rankings:UserRankingList,
		anime_list:AnimeListClean,
		)->Tuple[UserListPreFilter, UserListPreFilterOut]:
	''' Exclude all rankings which do not include an anime id from the anime_list.'''
	_logger.debug('prefilter_rankings()')
	ranking_frame = raw_rankings.get_frame().copy()
	anime_ids = anime_list.get_frame()[AnimeListColumns.ANIME_ID]

	# If the ANIME ID is in the anime_list, keep the record. Or maybe we make an entirely separate frame after filtering.
	# If we do not perform this filter, we have a lot of data we consider semi-irrelevant. But that information is usefful in understanding a user?
	select_invalid_ranks = ~(ranking_frame[UserRankingColumn.ANIME_ID].isin(anime_ids))
	removal_list = ranking_frame.loc[select_invalid_ranks]
	ranking_frame.drop(index=removal_list.index, inplace=True)
	ULFP = UserListPreFilter(frame=ranking_frame)
	ULFPO = UserListPreFilterOut(frame=removal_list)
	return ULFP, ULFPO

def clean_rankings(ranking:UserListPreFilter)->Tuple[UserListClean, UserListCleanOut]:
	_logger.debug('clean_rankings()')
	frame = ranking.get_frame().copy()
	invalid_score = frame.loc[ # Score out of bounds or null.
		(
			(frame[UserRankingColumn.SCORE].isnull())
			| (frame[UserRankingColumn.SCORE]>10)
			| (frame[UserRankingColumn.SCORE]<0) # We allow 0, because they may not have rated it. Decide later what to do.
		)
	]
	invalid_status = frame.loc[
		(
			frame[UserRankingColumn.STATUS].isnull() # No status val
			| ~(frame[UserRankingColumn.STATUS].isin([m.value for m in StatusEnum])) # invalid status val
		)
	]
	'''TODO:
	- STATUS=COMPLETE and WATCHED_EPISODES > AnimeList[AnimeID].WatchedEpisodes, update from animelist
		- OR If status=Complete, just set watched episodes the AnimeList[AnimeID]
	'''
	# Collate removed data & drop from frame.
	output:List[str] = [
		f'Records where score is out-of-bounds: {invalid_score.shape[0]}',
		f'Records where status is null {invalid_status.shape[0]}'
	]
	_logger.info(f'Cleaning: {'\n\t'.join(output)}')
	removed = pd.concat([
		invalid_score,
		invalid_status
	])
	frame.drop(index=removed.index, inplace=True)
	# if save_to_csv:
	# 	_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_CLEAN)).mkdir(
	# 		# Create dir if it does not exist.
	# 		mode=0o775, parents=True,exist_ok=True
	# 	)
	# 	frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED),index=False)
	# 	removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED_OUT),index=False)
	ULC = UserListClean(frame=frame)
	ULCO = UserListCleanOut(frame=removed)
	return ULC, ULCO

def filter_rankings(cleaned_rankings:UserListClean)->Tuple[UserListFilter,UserListFilterOut]:
	''' Filters based on criteria. Aka the Post Filter. '''
	_logger.debug('filter_rankings()')
	frame = cleaned_rankings.get_frame().copy()
	'''TODO
	- [ ] Status
		- Remove PTW
		- Remove Currently watching & watched < 0.50?
		- Removed dropped where they did not watch until a threashold?
	- [ ] WATCHED_EPISODES
		- Watched Episodes = 0, drop
	'''
	rm_plan_to_watch = frame.loc[frame[UserRankingColumn.STATUS]==StatusEnum.PLAN_TO_WATCH]
	# Collate removed data & drop from frame.
	removed = pd.concat([
		rm_plan_to_watch,
	])
	frame.drop(index=removed.index, inplace=True)
	ULF = UserListFilter(frame=frame)
	ULFO = UserListFilterOut(frame=frame)
	return ULF, ULFO

def run():
	_logger.info('Begin.')
	folders:List[str] = [
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_CLEAN),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_FILTER),
		get_env_val_safe(EnvFields.DIR_RANKING_DATASETS)
	]
	for folder in folders:
		_logger.info(f'try-create folder: {folder}')
		Path(folder).mkdir(mode=0o775, parents=False, exist_ok=True)

	SUBSET_NROWS:Final[int] = int(ranking_list_raw_len)
	_logger.info('Fetch raw user_rankings and the clean anime_list')
	user_rankings = UserRankingList(nrows=SUBSET_NROWS,usecols=ranking_list_columns_for_retrieval)
	anime_list = AnimeListClean(usecols=[AnimeListColumns.ANIME_ID])

	# order of operations
	# - FILTER_1 (filters by anime_list)
	# - CLEAN_1 (removes invalid records)
	# - FILTER_2 (filters to what we want)
	sw = Stopwatch()

	# PRE FILTER - Remove records where the ANIME_ID is not found in our cleaned anime list
	_logger.info('Perform Prefiltering on raw data... (The removal of anime_id not found in our clean dataset).')	
	sw.start()
	pref,prefo = prefilter_rankings(
		raw_rankings=user_rankings, anime_list=anime_list
	)
	sw.end()
	_logger.info(f'Prefiltering(1) took: {str(sw)}')

	_logger.info('Perform cleaning on prefiltered data...')
	sw.start()
	clean, cleanedOut = clean_rankings(ranking=pref)
	sw.end()
	_logger.info(f'Cleaning(2) took: {str(sw)}')

	
	_logger.info('Perform filtering on cleaned data...')
	sw.start()
	filtered, filteredOut = filter_rankings(cleaned_rankings=clean)
	sw.end()
	_logger.info(f'Filtering(3) took: {str(sw)}')

	# Print differecnes
	output:List[str] = [
		'\nLengths of each list:',
		f'0\tRaw Rankings: {user_rankings.get_frame().shape[0]}',
		f'1\tPrefiltered: {pref.get_frame().shape[0]}',
		f'2\tCleaned: {clean.get_frame().shape[0]}',
		f'3\tFiltered: {filtered.get_frame().shape[0]}',
	]
	_logger.info('\n'.join(output))
	# ---
	_logger.info('End.')
	return