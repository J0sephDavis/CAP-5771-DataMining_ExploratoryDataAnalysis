from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from dataset.dataset import DatasetCSV as _DatasetCSV

from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	Tuple as _Tuple,
	List as _List,
	Union as _Union,
)
from dataset.plotting import PlotTSNE, PlotUMAP
from .filter import AnimeListFiltered as _AnimeListFiltered
from .dataset import AnimeListColumns as _AnimeListColumns
import logging as _logging
from helpers.context import APP_LOGGER_NAME as _APP_LOGGER_NAME
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.AnimeList.clean')
class AnimeListClean(_DatasetCSV, PlotTSNE, PlotUMAP):
	''' The AnimeList that has been cleaned. '''
	def __init__(self,
			  	frame:_Optional[_pd.DataFrame]=None,
			  	path:_Path = _Path(_get_env_val_safe(_EnvFields.CSV_ANIME_CLEAN)),
				usecols:_Optional[_List[_Union[str,_AnimeListColumns]]] = None
			  ) -> None:
		super().__init__(frame, path)
		_logger.debug(f'AnimeListClean.__init__(frame:{frame},path:{path})')
		if self.frame is None:
			_logger.debug('attempting to load csv')
			self.load(usecols=usecols)
	
	def plot_umap_transform_data(self):
		return self.plot_tsne_transform_data()
	
	def plot_tsne_transform_data(self) -> _Tuple[_pd.DataFrame,_pd.DataFrame]:
		_logger.info('AnimeListClean.plot_tsne_transform_data')
		select_columns:_List[str] = [
			_AnimeListColumns.ANIME_ID,
			_AnimeListColumns.TITLE,
			_AnimeListColumns.GENRE,
			_AnimeListColumns.TYPE,
		];
		frame = self.get_frame().copy()[select_columns]
		genre_cols = frame['genre'].str.get_dummies(sep=',')
		frame.drop(columns=['genre'],inplace=True)
		frame = frame.join(genre_cols)

		data = frame.drop(columns=[
			_AnimeListColumns.TITLE,
			_AnimeListColumns.ANIME_ID,
			_AnimeListColumns.TYPE
		]
		).apply(_pd.Series.value_counts)
		data = data.transpose()
		nrows = frame.shape[0]
		frame.drop(columns=data.loc[(data[1]<nrows*0.03) | (data[0]<nrows*0.03)].index, inplace=True)
		cols = [
			_AnimeListColumns.TITLE,
			_AnimeListColumns.TYPE
		]
		partial_frame = frame.copy()[cols]
		frame.drop(columns=cols,inplace=True)
		return frame, partial_frame

class AnimeListCleanOut(_DatasetCSV):
	''' The AnimeList records that have been cleaned out. '''
	def __init__(self,
			  frame:_Optional[_pd.DataFrame] = None,
			  path:_Path = _Path(_get_env_val_safe(_EnvFields.CSV_ANIME_CLEAN_OUT))
			) -> None:
		super().__init__(frame, path)
		_logger.debug(f'AnimeListClean.__init__(frame:{frame},path:{path})')
		if self.frame is None:
			_logger.debug('attempting to load csv')
			self.load()
	

def clean_dataset(anime_list:_AnimeListFiltered)->_Tuple[AnimeListClean, AnimeListCleanOut]:
	''' Apply cleaning rules to the AnimeList dataset. Return the clean set & the records that were removed. '''
	_logger.debug('clean_dataset()')
	frame = anime_list.get_frame().copy()
	impossible_score:_pd.Series[bool] = (frame['score']<1)|(frame['score']>10)|(frame['score'].isnull())
	no_members:_pd.Series[bool] = (frame['members']==0)|(frame['members'].isnull())
	invalid_status:_pd.Series[bool] = (frame['status'].isnull())
	no_genre:_pd.Series[bool] = (frame['genre'].isnull())
	REMOVE = (impossible_score | no_members | invalid_status | no_genre)
	removed = frame.loc[REMOVE].copy()
	frame.drop(index=removed.index,inplace=True)
	return AnimeListClean(frame=frame), AnimeListCleanOut(frame=removed)