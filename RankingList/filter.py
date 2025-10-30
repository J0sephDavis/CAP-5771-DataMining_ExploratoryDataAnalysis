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

def filter_dataset(raw_frame:_pd.DataFrame):
	raise NotImplementedError()
	return raw_frame