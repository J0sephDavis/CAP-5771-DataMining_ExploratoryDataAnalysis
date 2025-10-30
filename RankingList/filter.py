from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from .dataset import (
	UserRankingColumn as _UserRankingColumn,
	StatusEnum as _StatusEnum,
)
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Union as _Union,
)
from helpers.files import get_dataset as _get_dataset
def get_dataset(nrows:_Optional[int]=None, use_cols:_Optional[_List[_Union[_UserRankingColumn,str]]]=None)->_pd.DataFrame:
	''' Reads the user ranking list from CSV & returns a dataframe. '''
	ranking_file = _Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED))
	return _get_dataset(
		file=ranking_file,
		nrows=nrows,
		use_cols=use_cols
	)
	
def get_dataset_out(nrows:_Optional[int]=None, use_cols:_Optional[_List[_Union[_UserRankingColumn,str]]]=None)->_pd.DataFrame:
	return _get_dataset(
		file=_Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED_OUT)),
		nrows=nrows,
		use_cols=use_cols
	)

from AnimeList.dataset import AnimeListColumns as _AnimeListColumns




def pre_filter_dataset(raw_rankings:_pd.DataFrame, anime_list:_pd.DataFrame, save_to_csv:bool):
	''' Just filters based on the anime_list dataset to remove irrelevant records.'''
	frame = raw_rankings.copy()

	# If the ANIME ID is in the anime_list, keep the record. Or maybe we make an entirely separate frame after filtering.
	# If we do not perform this filter, we have a lot of data we consider semi-irrelevant. But that information is usefful in understanding a user?
	rm_bad_anime_id = raw_rankings.loc[~(raw_rankings[_UserRankingColumn.ANIME_ID].isin(anime_list[_AnimeListColumns.ANIME_ID]))]
	
	frame.drop(index=rm_bad_anime_id.index, inplace=True)
	if save_to_csv:
		_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_FILTER)).mkdir(
			mode=0o775, parents=True,exist_ok=True
		)
		frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED_PRE),index=False)
		rm_bad_anime_id.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED_PRE_OUT),index=False)
	return frame, rm_bad_anime_id

def filter_dataset(cleaned_rankings:_pd.DataFrame, anime_list:_pd.DataFrame, save_to_csv:bool):
	''' Filters based on criteria. Aka the Post Filter. '''
	frame = cleaned_rankings.copy()
	'''TODO
	- [ ] Status
		- Remove PTW
		- Remove Currently watching & watched < 0.50?
		- Removed dropped where they did not watch until a threashold?
	- [ ] WATCHED_EPISODES
		- Watched Episodes = 0, drop
	'''
	rm_plan_to_watch = frame.loc[frame[_UserRankingColumn.STATUS]==_StatusEnum.PLAN_TO_WATCH]
	# Collate removed data & drop from frame.
	removed = _pd.concat([
		rm_plan_to_watch,
	])
	frame.drop(index=removed.index, inplace=True)
	if save_to_csv:
		_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_FILTER)).mkdir(
			mode=0o775, parents=True,exist_ok=True
		)
		frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED),index=False)
		removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED_OUT),index=False)
	return frame, removed