from helpers.context import get_env_val_safe,EnvFields
from pathlib import Path
import pandas as pd
from typing import Optional, List, Final
from enum import StrEnum
from RankingList import (
	dataset,
	filter,
	clean,
)

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

def run():
	SUBSET_NROWS:Final[int] = int(dataset.raw_dataset_length)
	import time
	print('get user rankings')
	time_start = time.time()
	user_rankings = dataset.get_user_rankings(
		nrows = SUBSET_NROWS, # load a fraction of the dataset
		use_cols = dataset.columns_for_retrieval
	)
	time_end = time.time()
	print(f'loaded user rankings in: {time_end-time_start} seconds')
	import AnimeList.clean
	from AnimeList.dataset import AnimeListColumns
	print('get anime list')
	anime_list:pd.DataFrame = AnimeList.clean.get_clean_dataset(None,[AnimeListColumns.ANIME_ID])

	# order of operations
	# - FILTER_1 (filters by anime_list)
	# - CLEAN_1 (removes invalid records)
	# - FILTER_2 (filters to what we want)

	# PRE FILTER - Remove records where the ANIME_ID is not found in our cleaned anime list
	try:
		print('> Try load pre filter dataset from file')
		pre_filtered = filter.get_dataset()
		pre_filtered_out = filter.get_dataset_out()
		print('Loaded pre filter dataset from disk.')
	except FileNotFoundError:
		print('> pre Filter')
		time_start = time.time()
		pre_filtered, pre_filtered_out = filter.pre_filter_dataset(user_rankings,anime_list,False)
		time_end = time.time()
		print(f'PRE Filtered rankings in: {time_end-time_start} seconds')
		print(f'PRE Filtering removed: {100.0*(pre_filtered_out.shape[0]/user_rankings.shape[0]):.2f}% ({pre_filtered_out.shape[0]}) of records')

	# CLEAN - Remove invalid/impossible values & replace values where we can.
	try:
		print('> Try load clean dataset from file')
		cleaned = clean.get_dataset()
		cleaned_out = clean.get_dataset_out()
		print('Loaded clean dataset from disk.')
	except FileNotFoundError:
		print('> Clean')
		time_start = time.time()
		cleaned,cleaned_out = clean.clean_dataset(pre_filtered, anime_list, False)
		time_end = time.time()
		print(f'Cleaned rankings in: {time_end-time_start} seconds')
		print(f'Cleaning removed: {100.0*(cleaned_out.shape[0]/pre_filtered.shape[0]):.2f}% ({cleaned.shape[0]}) of records')

	# POST FILTER - Get only the records we care about
	try:
		print('> Try load pre filter dataset from file')
		filtered = filter.get_dataset()
		filtered_out = filter.get_dataset_out()
		print('Loaded pre filter dataset from disk.')
	except FileNotFoundError:
		print('> pre Filter')
		time_start = time.time()
		filtered, filtered_out = filter.pre_filter_dataset(user_rankings,anime_list,False)
		time_end = time.time()
		print(f'PRE Filtered rankings in: {time_end-time_start} seconds')
		print(f'PRE Filtering removed: {100.0*(filtered_out.shape[0]/cleaned.shape[0]):.2f}% ({filtered_out.shape[0]}) of records')
	return