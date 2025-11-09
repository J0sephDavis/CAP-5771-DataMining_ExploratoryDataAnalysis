import logging as _logging
from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
)
from dataset.dataset import DatasetCSV as _DatasetCSV
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.filter')

class UserListFilter(_DatasetCSV):
	''' The user list with a default subset selected'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKING_FILTER)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
	
class UserListFilterOut(_DatasetCSV):
	''' The user list with a default subset selected'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKING_FILTER_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)