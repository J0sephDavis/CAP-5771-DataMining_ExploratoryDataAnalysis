from helpers.context import (
	load_find_env as _load_find_env,
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from . import dataset as _dataset
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Final as _Final,
)
from enum import (
	StrEnum as _StrEnum,
)

def get_dataset(nrows:_Optional[int], use_cols:_Optional[_List[_dataset.UserRankingColumn]])->_pd.DataFrame:
	''' Reads the user ranking list from CSV & returns a dataframe. '''
	ranking_file = _Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED))
	if not ranking_file.exists():
		raise FileNotFoundError('Ranking File does not exist.')
	return _pd.read_csv(
		filepath_or_buffer=ranking_file,
		nrows=nrows,
		usecols=use_cols
	)

def filter_dataset(raw_frame:_pd.DataFrame):
	raise NotImplementedError()
	return raw_frame