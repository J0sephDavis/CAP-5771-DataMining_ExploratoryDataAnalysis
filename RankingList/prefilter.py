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
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.prefilter')

class UserListPreFilter(_DatasetCSV):
	''' The user list that has only removed records based on anime ID.
	This is a costly check, so we save a copy before we go on to test copy implementations
	'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKINGS_PREFILTER)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

class UserListPreFilterOut(_DatasetCSV):
	''' The records with excluded anime. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKINGS_PREFILTER_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
