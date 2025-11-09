from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from helpers.files import DatasetBase as _DatasetBase
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	Tuple as _Tuple,
)
from .filter import AnimeListFiltered as _AnimeListFiltered

class AnimeListClean(_DatasetBase):
	''' The AnimeList that has been cleaned. '''
	def __init__(self,
		frame:_Optional[_pd.DataFrame] = None,
		nrows:_Optional[int] = None
			)->None:
		super().__init__(
			path=_Path(_get_env_val_safe(_EnvFields.CSV_ANIME_CLEAN)),
			frame=frame,
			nrows=nrows,
		)

class AnimeListCleanOut(_DatasetBase):
	''' The AnimeList records that have been cleaned out. '''
	def __init__(self,
		frame:_Optional[_pd.DataFrame] = None,
		nrows:_Optional[int] = None
			)->None:
		super().__init__(
			path=_Path(_get_env_val_safe(_EnvFields.CSV_ANIME_CLEAN_OUT)),
			frame=frame,
			nrows=nrows,
		)
def clean_dataset(anime_list:_AnimeListFiltered)->_Tuple[AnimeListClean, AnimeListCleanOut]:
	''' Apply cleaning rules to the AnimeList dataset. Return the clean set & the records that were removed. '''
	frame = anime_list.get_frame().copy()
	impossible_score:_pd.Series[bool] = (frame['score']<1)|(frame['score']>10)|(frame['score'].isnull())
	no_members:_pd.Series[bool] = (frame['members']==0)|(frame['members'].isnull())
	invalid_status:_pd.Series[bool] = (frame['status'].isnull())
	no_genre:_pd.Series[bool] = (frame['genre'].isnull())
	REMOVE = (impossible_score | no_members | invalid_status | no_genre)
	removed = frame.loc[REMOVE].copy()
	frame.drop(index=removed.index,inplace=True)
	return AnimeListClean(frame=frame), AnimeListCleanOut(frame=removed)