__all__ = [
	'clean',
	'filter',
	'plots',
	'comparison'
]
from pathlib import Path
import pandas as pd
from typing import List, Optional
from helpers.context import EnvRequiredFields,get_env_val_safe
from enum import StrEnum,auto

ANIME_USE_COLUMNS:List[str] = [ # The columns used when reading the file.
	'anime_id',	# PK
	# 'title',	# Used when deciphering results later
	# 'episodes',	# Used in calculating some values in the ranking list
	'status', 	# Only used in filtering
	
	'type',		# Filtering + analysis
	'genre',	# Used in clustering later. Prime descriptor of content

 	'score', 	# !!!! Predictor
	'scored_by',
	
	'rank',
	'popularity',
	
	'members',
	'favorites',
]

class DatasetDescriptors(StrEnum):
	ColumnName='DATASET_DESCRIPTOR'
	Filtered = 'Filtered'
	Raw = 'Raw'
	Cleaned = 'Cleaned'

def get_dataset(nrows:Optional[int] = None, use_cols:Optional[List[str]] = ANIME_USE_COLUMNS)->pd.DataFrame:
	""" Load the AnimeList.csv dataset into a dataframe """
	PATH_TO_DATASET = get_env_val_safe(EnvRequiredFields.ANIME_LIST)
	if not Path(PATH_TO_DATASET).exists():
		raise FileNotFoundError(f'Dataset not found @ {PATH_TO_DATASET}')
	frame = pd.read_csv(
		filepath_or_buffer=PATH_TO_DATASET,
		nrows=nrows,
		usecols=use_cols
	)
	return frame

def get_filtered_anime_dataset(nrows:Optional[int]=None)->pd.DataFrame:
	''' If the dataset exists, reads it into a dataframe. err otherwise '''
	PATH_TO_FILTERED = get_env_val_safe(EnvRequiredFields.ANIME_FILTERED)
	if not Path(PATH_TO_FILTERED).exists():
		raise FileNotFoundError(f'Dataset not found @ {PATH_TO_FILTERED}')
	return pd.read_csv(PATH_TO_FILTERED,nrows=nrows)

def get_cleaned_anime_dataset(nrows:Optional[int]=None)->pd.DataFrame:
	''' If the dataset exists, reads it into a dataframe. err otherwise '''
	PATH_TO_CLEANED = get_env_val_safe(EnvRequiredFields.ANIME_CLEANED)
	if not Path(PATH_TO_CLEANED).exists():
		raise FileNotFoundError(f'Dataset not found @ {PATH_TO_CLEANED}')
	return pd.read_csv(PATH_TO_CLEANED,nrows=nrows)