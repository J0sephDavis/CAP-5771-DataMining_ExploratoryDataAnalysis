import logging as _logging
from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from .dataset import (
	UserRankingColumn as _UserRankingColumn,
	StatusEnum as _StatusEnum,
)
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Union as _Union,
	Tuple as _Tuple,
)
from dataset.dataset import DatasetCSV as _DatasetCSV
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.RankingList.filter')

from RankingList.dataset import (
	UserRankingList as UserRankingList
)
from RankingList.clean import (
	UserListClean as UserListClean
)

from AnimeList.dataset import AnimeListColumns as _AnimeListColumns
from AnimeList.clean import AnimeListClean as _AnimeListClean

class UserListFilter(_DatasetCSV):
	''' The user list with a default subset selected'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

	@staticmethod
	def from_clean(cleaned_rankings:UserListClean)->_Tuple['UserListFilter','UserListFilterOut']:
		''' Filters based on criteria. Aka the Post Filter. '''
		frame = cleaned_rankings.get_frame().copy()
		'''TODO
		- [ ] Status
			- Remove PTW
			- Remove Currently watching & watched < 0.50?
			- Removed dropped where they did not watch until a threashold?
		- [ ] WATCHED_EPISODES
			- Watched Episodes = 0, drop
		'''
		rm_plan_to_watch = frame.loc[frame[_UserRankingColumn.STATUS]==_StatusEnum.PLAN_TO_WATCH]
		# Collate removed data & drop from frame.
		removed = _pd.concat([
			rm_plan_to_watch,
		])
		frame.drop(index=removed.index, inplace=True)
		# if save_to_csv:
		# 	_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_FILTER)).mkdir(
		# 		mode=0o775, parents=True,exist_ok=True
		# 	)
		# 	frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED),index=False)
		# 	removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_FILTERED_OUT),index=False)
		ULF = UserListFilter(frame=frame)
		ULFO = UserListFilterOut(frame=frame)
		return ULF, ULFO
	
class UserListFilterOut(_DatasetCSV):
	''' The user list with a default subset selected'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)


class UserListPreFilter(_DatasetCSV):
	''' The user list that has only removed records based on anime ID.
	This is a costly check, so we save a copy before we go on to test copy implementations
	'''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED_PRE)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

	@staticmethod
	def from_rankings(
			raw_rankings:UserRankingList,
			anime_list:_AnimeListClean,
			)->_Tuple['UserListPreFilter', 'UserListPreFilterOut']:
		''' Exclude all rankings which do not include an anime id from the anime_list.'''
		_logger.info('UserListPreFilter#pre_filter_dataset')
		ranking_frame = raw_rankings.get_frame().copy()
		anime_ids = anime_list.get_frame()[_AnimeListColumns.ANIME_ID]

		# If the ANIME ID is in the anime_list, keep the record. Or maybe we make an entirely separate frame after filtering.
		# If we do not perform this filter, we have a lot of data we consider semi-irrelevant. But that information is usefful in understanding a user?
		select_invalid_ranks = ~(ranking_frame[_UserRankingColumn.ANIME_ID].isin(anime_ids))
		removal_list = ranking_frame.loc[select_invalid_ranks]
		ranking_frame.drop(index=removal_list.index, inplace=True)
		ULFP = UserListPreFilter(frame=ranking_frame)
		ULFPO = UserListPreFilterOut(frame=removal_list)
		
		# _Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_FILTER)).mkdir(
		# 	mode=0o775, parents=True,exist_ok=True
		# )
		# ULF.save(index=False)
		# ULFO.save(index=False)
		return ULFP, ULFPO

class UserListPreFilterOut(_DatasetCSV):
	''' The records with excluded anime. '''
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=_Path(_get_env_val_safe(_EnvFields.RANKING_FILTERED_PRE_OUT)),
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
