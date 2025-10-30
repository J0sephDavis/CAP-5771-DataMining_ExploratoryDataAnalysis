from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from .dataset import UserRankingColumn as _UserRankingColumn
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Final as _Final,
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
def filter_dataset(raw_rankings:_pd.DataFrame, anime_list:_pd.DataFrame):
	frame = raw_rankings.copy()

	# If the ANIME ID is in the anime_list, keep the record. Or maybe we make an entirely separate frame after filtering.
	# If we do not perform this filter, we have a lot of data we consider semi-irrelevant. But that information is usefful in understanding a user?
	rm_bad_anime_id = raw_rankings.loc[~(raw_rankings[_UserRankingColumn.ANIME_ID].isin(anime_list[_AnimeListColumns.ANIME_ID]))]

	# Collate removed data & drop from frame.
	removed = _pd.concat([
		rm_bad_anime_id
	])
	frame.drop(index=removed.index, inplace=True)
	RANKING_FILTERED = _Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_FILTER))
	RANKING_FILTERED.mkdir(mode=0o775, parents=True,exist_ok=True)
	frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED),index=False)
	removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED_OUT),index=False)
	return frame, removed