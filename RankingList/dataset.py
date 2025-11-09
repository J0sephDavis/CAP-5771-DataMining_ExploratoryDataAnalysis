import logging as _logging
from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from dataset.dataset import DatasetCSV as _DatasetCSV
from pathlib import (
	Path as _Path
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Final as _Final,
	Union as _Union,
)
from enum import (
	StrEnum as _StrEnum,
	IntEnum as _IntEnum
)

_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.dataset')

class UserRankingColumn(_StrEnum):
	''' Column names from the dataset. '''
	USERNAME			='username'
	ANIME_ID			='anime_id'				
	WATCHED_EPISODES	='my_watched_episodes'
	START_DATE			='my_start_date'		# Many 0000-00-00
	FINISH_DATE			='my_finish_date'		# Many 0000-00-00
	SCORE				='my_score'
	STATUS				='my_status'
	REWATCHING			='my_rewatching'		# Missing some values
	REWATCHING_EP		='my_rewatching_ep'		# Many 0
	LAST_UPDATED		='my_last_updated'
	TAGS				='my_tags'				# Majority missing

class StatusEnum(_IntEnum):
	WATCHING=1
	COMPLETED=2
	ON_HOLD=3
	DROPPED=4
	PLAN_TO_WATCH=6

ranking_list_raw_len:_Final[int] = 80076112
columns_for_retrieval:_Final[_List[_Union[UserRankingColumn,str]]] = [
	UserRankingColumn.ANIME_ID,
	UserRankingColumn.USERNAME,
	UserRankingColumn.WATCHED_EPISODES,
	UserRankingColumn.SCORE,
	UserRankingColumn.STATUS
]

class UserRankingList(_DatasetCSV):
	''' The user list with a default subset selected'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_LIST)),
				nrows:_Optional[int] = None,
				usecols:_Optional[_List[_Union[UserRankingColumn,str]]] = columns_for_retrieval
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserList.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(usecols=usecols, nrows=nrows)