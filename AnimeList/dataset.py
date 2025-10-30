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
)
from enum import (
	StrEnum as _StrEnum
)

class AnimeListColumns(_StrEnum):
	''' Column names from the dataset. '''
	ANIME_ID='anime_id'
	TITLE='title'
	TITLE_ENGLISH='title_english'
	TITLE_JAPANESE='title_japanese'
	TITLE_SYNONYMS='title_synonyms'
	IMAGE_URL='image_url'
	TYPE='type'
	SOURCE='source'
	EPISODES='episodes'
	STATUS='status'
	AIRING='airing'
	AIRED_STRING='aired_string'
	AIRED='aired'
	DURATION='duration'
	RATING='rating'
	SCORE='score'
	SCORED_BY='scored_by'
	RANK='rank'
	POPULARITY='popularity'
	MEMBERS='members'
	FAVORITES='favorites'
	BACKGROUND='background'
	PREMIERED='premiered'
	BROADCAST='broadcast'
	RELATED='related'
	PRODUCER='producer'
	LICENSOR='licensor'
	STUDIO='studio'
	GENRE='genre'
	OPENING_THEME='opening_theme'
	ENDING_THEME='ending_theme'

columns_for_retrieval:_Final[_List[_Union[AnimeListColumns,str]]] = [
	AnimeListColumns.ANIME_ID,
	AnimeListColumns.STATUS,
	AnimeListColumns.TYPE,
	AnimeListColumns.GENRE,
	AnimeListColumns.SCORE,
	AnimeListColumns.SCORED_BY,
	AnimeListColumns.RANK,
	AnimeListColumns.POPULARITY,
	AnimeListColumns.MEMBERS,
	AnimeListColumns.FAVORITES,
]

def get_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[AnimeListColumns,str]]] = columns_for_retrieval
	)->_pd.DataFrame:
	''' Load the AnimeList.csv dataset into a dataframe. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_LIST))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)