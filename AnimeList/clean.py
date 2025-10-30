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
	Sequence as _Sequence,
	Final as _Final,
	Union as _Union,
	Tuple as _Tuple,
)
from enum import (
	StrEnum as _StrEnum
)
from . import dataset as _dataset

def get_clean_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[_dataset.AnimeListColumns,str]]] = None
	)->_pd.DataFrame:
	''' Load the clean dataset. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_CLEANED))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)

def get_out_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[_dataset.AnimeListColumns,str]]] = None
	)->_pd.DataFrame:
	''' Load the records that were REMOVED from the dataset during cleaning. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_CLEANED_OUT))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)


def clean_dataset(anime_list:_pd.DataFrame)->_Tuple[_pd.DataFrame, _pd.DataFrame]:
	''' Apply cleaning rules to the AnimeList dataset. Return the clean set & the records that were removed. '''
	frame = anime_list.copy()
	impossible_score:_pd.Series[bool] = (frame['score']<1)|(frame['score']>10)|(frame['score'].isnull())
	no_members:_pd.Series[bool] = (frame['members']==0)|(frame['members'].isnull())
	invalid_status:_pd.Series[bool] = (frame['status'].isnull())
	no_genre:_pd.Series[bool] = (frame['genre'].isnull())
	REMOVE = (impossible_score | no_members | invalid_status | no_genre)
	removed = frame.loc[REMOVE].copy()
	frame.drop(index=removed.index,inplace=True)
	return frame, removed