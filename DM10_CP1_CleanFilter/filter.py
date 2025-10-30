from plots import (
	comparison_barchart_by_type as _comparison_barchart_by_type,
	compare_by_group as _compare_by_group,
)
from helpers.context import (
	load_find_env as _load_find_env,
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from helpers import files as _files
from pathlib import (
	Path as _Path,
)
import pandas as _pd
from typing import (
	Tuple as _Tuple,
)
from AnimeList import (
	dataset as _dataset,
	filter as _filter,
	DatasetDescriptors as _DatasetDescriptors,
)
from AnimeList.dataset import AnimeListColumns as _AnimeListColumns

def filter_dataset(anime_list:_pd.DataFrame)->_Tuple[_pd.DataFrame,_pd.DataFrame]:
	"""
	Apply filtering rules to the AnimeList dataset.
	Returns the filtered frame & another frame containing the dropped records.
	"""
	frame = anime_list.copy()
	# Records
	removed_records = frame.loc[ # for analysis
		(frame['status'] != 'Finished Airing')
		| ((frame['type']=='Music') | (frame['type']=='Unknown'))
	].copy()

	frame.drop( # Remove all results which have not finished airing
		index=frame[frame['status']!='Finished Airing'].index,
		inplace=True
	)
	frame.drop( # Drop all results which are of type 'Music' or 'Unknown'.
		index=frame[(frame['type']=='Music')|(frame['type']=='Unknown')].index,
		inplace=True
	)
	return frame, removed_records

def generate_graph(load_env:bool):
	if load_env:
		_load_find_env()
	anime_raw = _dataset.get_dataset()
	
	RESULTS_FOLDER = _Path(_get_env_val_safe(_EnvFields.ANIME_CF_FOLDER_FILTERED))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)
	try:
		anime_filtered = _filter.get_dataset()
		anime_filtered_out = _filter.get_out_dataset()
	except FileNotFoundError as e:
		anime_filtered, anime_filtered_out = _filter.filter_dataset(anime_raw)
	
	anime_filtered[_DatasetDescriptors.ColumnName]=_DatasetDescriptors.Filtered
	anime_raw[_DatasetDescriptors.ColumnName]=_DatasetDescriptors.Raw

	filter_comparison_frame = _pd.concat([ # purely for comparison
		anime_raw.drop( # Cannot compare types which no longer exist.
			index=anime_raw[(anime_raw[_AnimeListColumns.TYPE]=='Music')|(anime_raw[_AnimeListColumns.TYPE]=='Unknown')].index
		),
		anime_filtered
	],axis=0)
	_compare_by_group(filter_comparison_frame, str(RESULTS_FOLDER))
	
	# Stacked barchart counting removed entities
	F01,F01_ax = _comparison_barchart_by_type(anime_filtered,anime_filtered_out)
	F01.suptitle('Filter Results')
	F01.savefig('{}/F01_filter_results.tiff'.format(RESULTS_FOLDER))

if __name__ == '__main__':
	generate_graph(True)