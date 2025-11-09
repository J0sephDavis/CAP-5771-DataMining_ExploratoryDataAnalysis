from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
	APP_LOGGER_NAME as _APP_LOGGER_NAME,
)
from helpers import files as _files
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
from .dataset import AnimeListColumns as _AnimeListColumns
from dataset.dataset import DatasetCSV as _DatasetCSV
from .dataset import AnimeListRaw as _AnimeListRaw
import logging as _logging
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.AnimeList.filter')
class AnimeListFiltered(_DatasetCSV):
	''' The AnimeList that has been filtered. '''
	def __init__(self,
			  frame:_Optional[_pd.DataFrame] = None,
			  path:_Path = _Path(_get_env_val_safe(_EnvFields.CSV_ANIME_FILTER))
			) -> None:
		_logger.debug(f'AnimeListFiltered.__init__(frame:{frame}, path:{path})')
		super().__init__(frame, path)
		if self.frame is None:
			_logger.debug('AnimeListFiltered.__init__: attempting to load csv')
			self.load()

class AnimeListFilterOut(_DatasetCSV):
	''' The AnimeList that has been filtered. '''
	def __init__(self,
			  frame:_Optional[_pd.DataFrame] = None,
			  path:_Path = _Path(_get_env_val_safe(_EnvFields.CSV_ANIME_FILTER_OUT))
			) -> None:
		_logger.debug(f'AnimeListFilterOut.__init__(frame:{frame}, path:{path})')
		super().__init__(frame, path)
		if self.frame is None:
			_logger.debug('AnimeListFilterOut.__init__: attempting to load csv')
			self.load()

def filter_dataset(anime_list:_AnimeListRaw)->_Tuple[AnimeListFiltered, AnimeListFilterOut]:
	'''
	Apply filtering rules to the AnimeList dataset.
	Returns the filtered frame & another frame containing the dropped records.
	'''
	_logger.debug('filter_dataset')
	frame = anime_list.get_frame()
	if frame is None:
		raise Exception('')
	frame = frame.copy()
	# Records
	removed_records = frame.loc[ # for analysis
		(frame[_AnimeListColumns.STATUS] != 'Finished Airing')
		| ((frame[_AnimeListColumns.TYPE]=='Music') | (frame[_AnimeListColumns.TYPE]=='Unknown'))
	].copy()

	frame.drop(index=removed_records.index, inplace=True)
	# ^^^ If this doesn't work, just uncomment below and delete it. Not testing today.
	# frame.drop( # Remove all results which have not finished airing
	# 	index=frame[frame[_AnimeListColumns.STATUS]!='Finished Airing'].index,
	# 	inplace=True
	# )
	# frame.drop( # Drop all results which are of type 'Music' or 'Unknown'.
	# 	index=frame[(frame[_AnimeListColumns.TYPE]=='Music')|(frame[_AnimeListColumns.TYPE]=='Unknown')].index,
	# 	inplace=True
	# )
	return AnimeListFiltered(frame=frame), AnimeListFilterOut(frame=removed_records)