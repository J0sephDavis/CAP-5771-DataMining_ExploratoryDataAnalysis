from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from helpers import files as _files
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Union as _Union,
	Tuple as _Tuple,
)
from .dataset import AnimeListColumns as _AnimeListColumns

def get_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[_AnimeListColumns,str]]] = None
	)->_pd.DataFrame:
	''' Load the filtered dataset. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)

def get_out_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[_AnimeListColumns,str]]] = None
	)->_pd.DataFrame:
	''' Load the records that were REMOVED from the dataset. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED_OUT))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)


def filter_dataset(anime_list:_pd.DataFrame)->_Tuple[_pd.DataFrame, _pd.DataFrame]:
	'''
	Apply filtering rules to the AnimeList dataset.
	Returns the filtered frame & another frame containing the dropped records.
	'''
	frame = anime_list.copy()
	# Records
	removed_records = frame.loc[ # for analysis
		(frame[_AnimeListColumns.STATUS] != 'Finished Airing')
		| ((frame[_AnimeListColumns.TYPE]=='Music') | (frame[_AnimeListColumns.TYPE]=='Unknown'))
	].copy()

	frame.drop(index=removed_records.index, inplace=True)
	# ^^^ If this doesn't work, just uncomment below and delete it. Not testing today.
	# frame.drop( # Remove all results which have not finished airing
	# 	index=frame[frame[_AnimeListColumns.STATUS]!='Finished Airing'].index,
	# 	inplace=True
	# )
	# frame.drop( # Drop all results which are of type 'Music' or 'Unknown'.
	# 	index=frame[(frame[_AnimeListColumns.TYPE]=='Music')|(frame[_AnimeListColumns.TYPE]=='Unknown')].index,
	# 	inplace=True
	# )
	return frame, removed_records