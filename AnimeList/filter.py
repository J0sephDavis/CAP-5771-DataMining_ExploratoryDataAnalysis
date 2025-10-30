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
from . import dataset as _dataset
def get_dataset(
		nrows:_Optional[int] = None,
		use_cols:_Optional[_List[_Union[_dataset.AnimeListColumns,str]]] = None
	)->_pd.DataFrame:
	''' Load the AnimeList.csv dataset into a dataframe. '''
	PATH_TO_DATASET = _Path(_get_env_val_safe(_EnvFields.ANIME_FILTERED))
	return _files.get_dataset(PATH_TO_DATASET, nrows=nrows, use_cols=use_cols)