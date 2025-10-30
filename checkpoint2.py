from helpers.context import load_find_env, get_env_val_safe,EnvFields
from pathlib import Path
import pandas as pd
from typing import Optional, List, Final
from enum import StrEnum
from RankingList import (
	dataset,
	filter,
	clean,
)
loaded, _ = load_find_env()
if not loaded:
	print('DOTENV could not be loaded. STOP.')
	exit()

''' TODO
- [ ] Fetch dataset

- [ ] Filter
	- [ ] ANIME_ID must be in our filtered & cleaned ANIME dataset.
	- [ ] 
- [ ] Clean
	- [ ] Remove invalid records
	- [ ] Fix invalid values, if we need to.

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
SUBSET_NROWS:Final[int] = int(dataset.raw_dataset_length)
import time
time_start = time.time()
user_rankings = dataset.get_user_rankings(
	nrows = SUBSET_NROWS, # load a fraction of the dataset
	use_cols = dataset.columns_for_retrieval
)
time_end = time.time()
print(f'loaded user rankings in: {time_end-time_start} seconds')
import AnimeList.clean
from AnimeList.dataset import AnimeListColumns
anime_list:pd.DataFrame = AnimeList.clean.get_clean_dataset(None,[AnimeListColumns.ANIME_ID])
try:
	filtered = filter.get_dataset()
	filtered_out = filter.get_dataset_out()
	print('Loaded filter from disk.')
except FileNotFoundError:
	time_start = time.time()
	filtered, filtered_out = filter.filter_dataset(user_rankings,anime_list)
	time_end = time.time()
	print(f'filtered rankings in: {time_end-time_start} seconds')
	print(f'Filtering removed: {100.0*(filtered_out.shape[0]/user_rankings.shape[0]):.2f}% ({filtered_out.shape[0]}) of records')

exit()