from pathlib import Path as _Path
import pandas as _pd
from typing import (
	Optional as _Optional,
)
from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from dataset.dataset import DatasetCSV as _DatasetCSV
from .prefilter import UserListPreFilter as UserListPreFilter

import logging as _logging
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.clean')


class UserListClean(_DatasetCSV):
	''' The user list cleaned. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKING_CLEAN)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListClean.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
	
class UserListCleanOut(_DatasetCSV):
	''' The records removed during cleaning. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.CSV_RANKING_CLEAN_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListCleanOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)