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
	columns_for_retrieval as ranking_list_columns_for_retrieval,
	UserListPreFilter,
	UserListClean,
	UserListFilter,
)
from RankingList.contentcontent import (
	ContentContentFrame
)
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
import gc
def _generate_datasets():
	generate_prefilter:bool = UserListPreFilter.default_path.exists()
	generate_clean:bool = generate_prefilter and UserListClean.default_path.exists()
	generate_filter:bool = generate_clean and UserListFilter.default_path.exists()

	sw = Stopwatch()
	pref:UserListPreFilter
	if generate_prefilter:
		_logger.info('Fetch raw user_rankings and the clean anime_list')
		sw.start()
		user_rankings = UserRankingList(nrows=None,usecols=ranking_list_columns_for_retrieval)
		sw.end()
		_logger.info(f'Loading user rankings took {str(sw)}')
		sw.start()
		anime_list = AnimeListClean(usecols=[AnimeListColumns.ANIME_ID])
		sw.end()
		_logger.info(f'Loading the anime list took {str(sw)}')

		# PRE FILTER - Remove records where the ANIME_ID is not found in our cleaned anime list
		_logger.info('Perform Prefiltering on raw data... (The removal of anime_id not found in our clean dataset).')	
		sw.start()
		pref,prefo = UserListPreFilter.prefilter_rankings(
			raw_rankings=user_rankings, anime_list=anime_list
		)
		sw.end()
		_logger.info(f'Prefiltering(1) took: {str(sw)}')
		rank_raw_len = user_rankings.get_frame().shape[0]
		del user_rankings
		gc.collect()
	elif generate_clean:
		pref = UserListPreFilter(frame=None)
	else:
		pref = None #  bs value to satisfy typesetter.
	
	clean:UserListClean
	if generate_clean:
		_logger.info('Perform cleaning on prefiltered data...')
		sw.start()
		clean, cleanedOut = UserListClean.clean_rankings(ranking=pref)
		sw.end()
		_logger.info(f'Cleaning(2) took: {str(sw)}')
		
		rank_pref_len = pref.get_frame().shape[0]
		pref.save()
		del pref
		gc.collect()
	elif generate_filter:
		clean = UserListClean(frame=None)
	else:
		clean = None # bs value to satisfy typesetter
	
	filter:UserListFilter
	if generate_filter:
		_logger.info('Perform filtering on cleaned data...')
		sw.start()
		filter, filteredOut = UserListFilter.filter_rankings(cleaned_rankings=clean)
		sw.end()
		_logger.info(f'Filtering(3) took: {str(sw)}')
		
		rank_clean_len = clean.get_frame().shape[0]
		clean.save()
		del clean
		gc.collect()
	else:
		filter = UserListFilter(frame=None)
	
	filter.save()
	return filter


def make_folders():
	folders:List[str] = [
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_CLEAN),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_FILTER),
		get_env_val_safe(EnvFields.DIR_RANKING_DATASETS)
	]
	for folder in folders:
		_logger.info(f'try-create folder: {folder}')
		Path(folder).mkdir(mode=0o775, parents=False, exist_ok=True)

def get_filtered_data():
	files:List[str] = [
		get_env_val_safe(EnvFields.CSV_RANKING_CLEAN),
		get_env_val_safe(EnvFields.CSV_RANKING_FILTER),
		get_env_val_safe(EnvFields.CSV_RANKINGS_PREFILTER),		
	]
	prefilter_clean_filter_data:bool = False
	for file in files:
		if not Path(file).exists():
			prefilter_clean_filter_data = True
			break
	filter:UserListFilter
	if prefilter_clean_filter_data:
		filter = _generate_datasets()
	else:
		filter = UserListFilter(frame=None)
	return filter
import surprise
def run():
	_logger.info('Begin.')
	make_folders()
	filter = get_filtered_data()
	# cbf:ContentContentFrame
	# if not ContentContentFrame.default_path.exists():
	# 	_logger.info('generating content collab frame')
	# 	frame = get_filtered_data().get_frame()[[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID]].copy()
	# 	gc.collect()
	# 	frame['value']=1
	# 	cbf = ContentContentFrame.from_filter(data=frame)
	# else:
	# 	sw = Stopwatch()
	# 	_logger.info('loading content collab frame from file')
	# 	sw.start()
	# 	cbf = ContentContentFrame(frame=None)
	# 	sw.end()
	# 	_logger.info(f'loading the cbf took {str(sw)}')

	reader = surprise.Reader(rating_scale=(1,10))
	prediction_frame = filter.get_frame()[[
		UserRankingColumn.USERNAME,
		UserRankingColumn.ANIME_ID,
		UserRankingColumn.SCORE
	]].copy()
	del filter
	gc.collect()
	_logger.info('RUN SVD ON ALGORITHM')
	sw = Stopwatch()
	sup_data = surprise.Dataset.load_from_df(reader=reader,df=prediction_frame)
	alg = surprise.SVD()
	sw.start()
	cross_validation_results = surprise.model_selection.cross_validate(
		algo=alg, data=sup_data, cv=5, verbose=False, n_jobs=-1
	)
	sw.end()
	_logger.info(f'cross validation took {str(sw)}')
	_logger.info('Cross-validation of SVD')
	for key,value in cross_validation_results.items():
		_logger.info(f'{key}\t{value}')
	# TODO:
	# matrix of USERS x Anime
	#	- row is a specific user
	#	- Column is a specifc anime
	# From this matrix
	#	- 1. I believe there was a method of modeling in one of our research papers using SVD
	#	- 2. Create a frequent pattern tree

	# How to use the cbf?

	_logger.info('End.')
	return