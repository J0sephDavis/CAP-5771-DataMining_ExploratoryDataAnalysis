from helpers.stopwatch import Stopwatch
from dataset.dataset import DatasetCSV
from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
from helpers.stopwatch import Stopwatch
from pathlib import Path
import pandas as pd
from typing import (
	Optional,
	List,
	Tuple,
	Final,
)
from RankingList.dataset import (
	UserRankingList,
	UserRankingColumn,
	StatusEnum,
	ranking_list_raw_len,
	columns_for_retrieval as ranking_list_columns_for_retrieval,
	UserListPreFilter,
	UserListPreFilterOut,
	UserListClean,
	UserListCleanOut,
	UserListFilter,
	UserListFilterOut,
)

from AnimeList.clean import AnimeListClean
from AnimeList.dataset import AnimeListColumns
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.RankingList.ContentContent')
import surprise
class ContentContentFrame(DatasetCSV):
	''' A dataframe that just represents implicit relationships.'''

	default_path:Final[Path] = Path('content-by-content.csv')
	def __init__(self, frame: Optional[pd.DataFrame], file: Path = default_path) -> None:
		super().__init__(frame, file)

	@classmethod
	def from_filter(cls,filter:Optional[UserListFilter], filepath:Path = default_path)->'ContentContentFrame':
		''' data dataframe of USERNAME,ANIME_ID'''
		if filter is None:
			filter = UserListFilter(frame=None)
		data = filter.get_frame()[[UserRankingColumn.USERNAME, UserRankingColumn.ANIME_ID, UserRankingColumn.SCORE]]

		sw = Stopwatch()
		sw.start()
		data['value']=1
		overlap_comparison = data.pivot_table(
			index=UserRankingColumn.USERNAME,
			columns=UserRankingColumn.ANIME_ID,
			values='value',
			fill_value=0,
		)
		sw.end()
		_logger.info(f'Generating content collaboration frame took {str(sw)}')
		sw.start()		
		overlap_comparison.to_csv(filepath, index=False)
		sw.end()
		_logger.info(f'Saving the frame took {str(sw)}')
		return cls(frame=overlap_comparison, file=filepath)