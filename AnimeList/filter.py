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
from helpers.files import DatasetBase as _DatasetBase

class AnimeListFilteted(_DatasetBase):
	''' The AnimeList that has been filtered. '''
	def __init__(self,
		frame:_Optional[_pd.DataFrame] = None,
		nrows:_Optional[int] = None
			)->None:
		super().__init__(
			path=_Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED)),
			frame=frame,
			nrows=nrows,
		)

class AnimeListFilterOut(_DatasetBase):
	''' The records that were filtered out of the AnimeList. '''
	def __init__(self,
		frame:_Optional[_pd.DataFrame],
		nrows:_Optional[int] = None
			) -> None:
		super().__init__(nrows=nrows,
			path=_Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED_OUT)),
			frame=frame,
		)

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
	frame.to_csv(_Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED)), index=False)
	removed_records.to_csv(_Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED_OUT)), index=False)
	return frame, removed_records