from pathlib import Path as _Path
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Tuple as _Tuple,
)
from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from .dataset import (
	UserRankingColumn as _UserRankingColumn,
	StatusEnum as _StatusEnum,
)
from dataset.dataset import DatasetCSV as _DatasetCSV
from .filter import UserListPreFilter as UserListPreFilter

import logging as _logging
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.clean')


class UserListClean(_DatasetCSV):
	''' The user list cleaned. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_CLEANED)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListClean.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

	@staticmethod
	def from_filter(ranking:UserListPreFilter)->_Tuple['UserListClean', 'UserListCleanOut']:
		frame = ranking.get_frame().copy()
		invalid_score = frame.loc[ # Score out of bounds or null.
			(
				(frame[_UserRankingColumn.SCORE].isnull())
				| (frame[_UserRankingColumn.SCORE]>10)
				| (frame[_UserRankingColumn.SCORE]<0) # We allow 0, because they may not have rated it. Decide later what to do.
			)
		]
		invalid_status = frame.loc[
			(
				frame[_UserRankingColumn.STATUS].isnull() # No status val
				| ~(frame[_UserRankingColumn.STATUS].isin([m.value for m in _StatusEnum])) # invalid status val
			)
		]
		'''TODO:
		- STATUS=COMPLETE and WATCHED_EPISODES > AnimeList[AnimeID].WatchedEpisodes, update from animelist
			- OR If status=Complete, just set watched episodes the AnimeList[AnimeID]
		'''
		# Collate removed data & drop from frame.
		output:_List[str] = [
			f'Records where score is out-of-bounds: {invalid_score.shape[0]}',
			f'Records where status is null {invalid_status.shape[0]}'
		]
		_logger.info(f'Cleaning: {'\n\t'.join(output)}')
		removed = _pd.concat([
			invalid_score,
			invalid_status
		])
		frame.drop(index=removed.index, inplace=True)
		# if save_to_csv:
		# 	_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_CLEAN)).mkdir(
		# 		# Create dir if it does not exist.
		# 		mode=0o775, parents=True,exist_ok=True
		# 	)
		# 	frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED),index=False)
		# 	removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED_OUT),index=False)
		ULC = UserListClean(frame=frame)
		ULCO = UserListCleanOut(frame=removed)
		return ULC, ULCO
	
class UserListCleanOut(_DatasetCSV):
	''' The records removed during cleaning. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_CLEANED_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListCleanOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)