from helpers.context import (
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from .dataset import (
	UserRankingColumn as _UserRankingColumn,
	MyStatus as _StatusEnum,
)
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Union as _Union,
)
from helpers.files import get_dataset as _get_dataset
def get_dataset(nrows:_Optional[int]=None, use_cols:_Optional[_List[_Union[_UserRankingColumn,str]]]=None)->_pd.DataFrame:
	''' Reads the user ranking list from CSV & returns a dataframe. '''
	ranking_file = _Path(_get_env_val_safe(_EnvFields.RANKING_CLEANED))
	return _get_dataset(
		file=ranking_file,
		nrows=nrows,
		use_cols=use_cols
	)
	
def get_dataset_out(nrows:_Optional[int]=None, use_cols:_Optional[_List[_Union[_UserRankingColumn,str]]]=None)->_pd.DataFrame:
	return _get_dataset(
		file=_Path(_get_env_val_safe(_EnvFields.RANKING_CLEANED_OUT)),
		nrows=nrows,
		use_cols=use_cols
	)

def clean_dataset(filtered_ranking:_pd.DataFrame, anime_List:_pd.DataFrame, save_to_csv:bool):
	frame = filtered_ranking.copy()
	rm_invalid_score = frame.loc[ # Score out of bounds or null.
		(
			(frame[_UserRankingColumn.SCORE].isnull())
			| (frame[_UserRankingColumn.SCORE]>10)
			| (frame[_UserRankingColumn.SCORE]<0) # We allow 0, because they may not have rated it. Decide later what to do.
		)
	]
	rm_invalid_status = frame.loc[
		(
			frame[_UserRankingColumn.STATUS].isnull() # No status val
			| ~(frame[_UserRankingColumn.STATUS].isin([m.value for m in _StatusEnum.__members__])) # invalid status val
		)
	]
	'''TODO:
	- STATUS=COMPLETE and WATCHED_EPISODES > AnimeList[AnimeID].WatchedEpisodes, update from animelist
		- OR If status=Complete, just set watched episodes the AnimeList[AnimeID]
	'''

	# Collate removed data & drop from frame.
	print('Cleaning:',
	   f'Records where score is out-of-bounds: {rm_invalid_score.shape[0]}',
	   f'Records where status is null {rm_invalid_status.shape[0]}',
	   sep='\n\t'
	)
	removed = _pd.concat([
		rm_invalid_score,
		rm_invalid_status
	])
	frame.drop(index=removed.index, inplace=True)
	if save_to_csv:
		_Path(_get_env_val_safe(_EnvFields.RANKING_FOLDER_CLEAN)).mkdir(
			# Create dir if it does not exist.
			mode=0o775, parents=True,exist_ok=True
		)
		frame.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED),index=False)
		removed.to_csv(_get_env_val_safe(_EnvFields.RANKING_CLEANED_OUT),index=False)
	return frame, removed