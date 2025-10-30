from helpers.context import load_find_env, get_env_val_safe,EnvFields
from pathlib import Path
import pandas as pd
from typing import Optional, List, Final
from enum import StrEnum
import DM14_CP2_UserRankings.dataset as dataset
loaded, _ = load_find_env()
if not loaded:
	print('DOTENV could not be loaded. STOP.')
	exit()

''' TODO
1. [ ] Fetch dataset
2. [ ] Filter and Clean
3. [ ] Boxplots for each feature
4. [ ] Measure covariance of features
5. [ ] Visualize covariant features
6. [ ] UMAP, TSNE of data
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
user_rankings = dataset.get_user_rankings(
	nrows = int(dataset.raw_dataset_length*0.15), # load a fraction of the dataset
	use_cols = dataset.columns_for_retrieval
)
exit()