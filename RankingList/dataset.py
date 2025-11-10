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
	Tuple as _Tuple,
	ClassVar as _ClassVar,
)
from enum import (
	StrEnum as _StrEnum,
	IntEnum as _IntEnum
)
from AnimeList.dataset import (
	AnimeListColumns as _AnimeListColumns
)
from AnimeList.clean import (
	AnimeListClean as _AnimeListClean
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
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.RANKING_LIST))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
				usecols:_Optional[_List[_Union[UserRankingColumn,str]]] = columns_for_retrieval
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserList.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(usecols=usecols, nrows=nrows)

# ------------------------------------------------------------------------------

class UserListPreFilterOut(_DatasetCSV):
	''' The records with excluded anime. '''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKINGS_PREFILTER_OUT))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

class UserListPreFilter(_DatasetCSV):
	''' The user list that has only removed records based on anime ID.
	This is a costly check, so we save a copy before we go on to test copy implementations
	'''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKINGS_PREFILTER))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame=frame, file=path)
		_logger.debug(f'UserListPreFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

	@staticmethod
	def prefilter_rankings(
			raw_rankings:_Optional[UserRankingList],
			anime_list:_Optional[_AnimeListClean],
		)->_Tuple['UserListPreFilter', UserListPreFilterOut]:
		''' Exclude all rankings which do not include an anime id from the anime_list.'''
		_logger.debug('prefilter_rankings()')
		if raw_rankings is None:
			raw_rankings = UserRankingList(frame=None)
		if anime_list is None:
			anime_list = _AnimeListClean(frame=None)
		
		ranking_frame = raw_rankings.get_frame().copy()
		anime_ids = anime_list.get_frame()[_AnimeListColumns.ANIME_ID]

		# If the ANIME ID is in the anime_list, keep the record. Or maybe we make an entirely separate frame after filtering.
		# If we do not perform this filter, we have a lot of data we consider semi-irrelevant. But that information is usefful in understanding a user?
		select_invalid_ranks = ~(ranking_frame[UserRankingColumn.ANIME_ID].isin(anime_ids))
		removal_list = ranking_frame.loc[select_invalid_ranks]
		ranking_frame.drop(index=removal_list.index, inplace=True)
		ULFP = UserListPreFilter(frame=ranking_frame)
		ULFPO = UserListPreFilterOut(frame=removal_list)
		return ULFP, ULFPO

# ------------------------------------------------------------------------------
	
class UserListCleanOut(_DatasetCSV):
	''' The records removed during cleaning. '''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKING_CLEAN_OUT))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListCleanOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

class UserListClean(_DatasetCSV):
	''' The user list cleaned. '''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKING_CLEAN))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListClean.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
	@staticmethod
	def clean_rankings(ranking:_Optional[UserListPreFilter])->_Tuple['UserListClean', UserListCleanOut]:
		if ranking is None:
			ranking = UserListPreFilter(frame=None)
		_logger.debug('clean_rankings()')
		frame = ranking.get_frame().copy()
		invalid_score = frame.loc[ # Score out of bounds or null.
			(
				(frame[UserRankingColumn.SCORE].isnull())
				| (frame[UserRankingColumn.SCORE]>10)
				| (frame[UserRankingColumn.SCORE]<0) # We allow 0, because they may not have rated it. Decide later what to do.
			)
		]
		invalid_status = frame.loc[
			(
				frame[UserRankingColumn.STATUS].isnull() # No status val
				| ~(frame[UserRankingColumn.STATUS].isin([m.value for m in StatusEnum])) # invalid status val
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
	
# ------------------------------------------------------------------------------
	
class UserListFilterOut(_DatasetCSV):
	''' The user list with a default subset selected'''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKING_FILTER_OUT))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilterOut.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)

class UserListFilter(_DatasetCSV):
	''' The user list with a default subset selected'''
	default_path:_ClassVar[_Path] = _Path(_get_env_val_safe(_EnvFields.CSV_RANKING_FILTER))
	def __init__(self,
				frame:_Optional[_pd.DataFrame]=None,
				path=default_path,
				nrows:_Optional[int] = None,
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'UserListFilter.__init__(frame:{frame}, path:{path})')
		if self.frame is None:
			self.load(nrows=nrows)
	
	@staticmethod
	def filter_rankings(cleaned_rankings:UserListClean)->_Tuple['UserListFilter',UserListFilterOut]:
		''' Filters based on criteria. Aka the Post Filter. '''
		_logger.debug('filter_rankings()')
		frame = cleaned_rankings.get_frame().copy()
		'''TODO
		- [ ] Status
			- Remove PTW
			- Remove Currently watching & watched < 0.50?
			- Removed dropped where they did not watch until a threashold?
		- [ ] WATCHED_EPISODES
			- Watched Episodes = 0, drop
		'''
		rm_plan_to_watch = frame.loc[frame[UserRankingColumn.STATUS]==StatusEnum.PLAN_TO_WATCH]
		# Collate removed data & drop from frame.
		removed = _pd.concat([
			rm_plan_to_watch,
		])
		frame.drop(index=removed.index, inplace=True)
		ULF = UserListFilter(frame=frame)
		ULFO = UserListFilterOut(frame=frame)
		return ULF, ULFO