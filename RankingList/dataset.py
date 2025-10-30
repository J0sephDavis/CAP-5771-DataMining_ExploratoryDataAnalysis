from helpers.context import (
	load_find_env as _load_find_env,
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields
)
from pathlib import (
	Path as _Path
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Final as _Final,
	Union as _Union,
)
from enum import (
	StrEnum as _StrEnum
)
from helpers.files import get_dataset as _get_dataset

class UserRankingColumn(_StrEnum):
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

raw_dataset_length:_Final[int] = 80076112
columns_for_retrieval:_Final[_List[_Union[UserRankingColumn,str]]] = [
	UserRankingColumn.ANIME_ID,
	UserRankingColumn.USERNAME,
	UserRankingColumn.WATCHED_EPISODES,
	UserRankingColumn.SCORE,
	UserRankingColumn.STATUS
]
def get_user_rankings(nrows:_Optional[int], use_cols:_Optional[_List[_Union[UserRankingColumn,str]]])->_pd.DataFrame:
	''' Reads the user ranking list from CSV & returns a dataframe. '''
	user_ranking_file = _Path(_get_env_val_safe(_EnvFields.RANKING_LIST))
	return _get_dataset(file=user_ranking_file, nrows=nrows, use_cols=use_cols)