from helpers.context import load_find_env, get_env_val_safe,EnvFields
from pathlib import Path
import pandas as pd
from typing import Optional, List, Final
from enum import StrEnum
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

class UserRankingColumn(StrEnum):
	''' Column names from the dataset. '''
	USERNAME			='username'
	ANIME_ID			='anime_id'				
	WATCHED_EPISODES	='my_watched_episodes'
	START_DATE			='my_start_date'		# Many 0000-00-00
	FINISH_DATE			='my_finish_date'		# Many 0000-00-00
	SCORE				='my_score'
	STATUS				='my_status'
	REWATCHING			='my_rewatching'		# Missing some values
	REWATCHING_EP		='my_rewatching_ep'		# Many 0
	LAST_UPDATED		='my_last_updated'
	TAGS				='my_tags'				# Majority missing

def get_user_rankings(nrows:Optional[int], use_cols:Optional[List[UserRankingColumn]])->pd.DataFrame:
	''' Reads the user ranking list from CSV & returns a dataframe. '''
	user_ranking_file:Path = Path(get_env_val_safe(EnvFields.RANKING_LIST))
	return pd.read_csv(
		filepath_or_buffer=user_ranking_file,
		nrows=nrows,
		usecols=use_cols
	)
