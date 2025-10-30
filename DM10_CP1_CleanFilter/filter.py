import os
from typing import Tuple,Optional
import pandas as pd
from pathlib import Path
from helpers.context import EnvFields,get_env_val_safe,load_find_env
from plots import comparison_barchart_by_type, compare_by_group
from __init__  import get_dataset,DatasetDescriptors

FOLDER_FILTER = Path('DM10_CP1_CleanFilter/Filtered')
FILE_FILTER = Path(f'{FOLDER_FILTER}{os.sep}anime_filtered.csv')

def filter_dataset(anime_list:pd.DataFrame)->Tuple[pd.DataFrame,pd.DataFrame]:
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
		load_find_env()
	anime_raw = get_dataset()
	
	RESULTS_FOLDER:Path = Path(get_env_val_safe(EnvFields.ANIME_CF_FOLDER_FILITED))
	FILTERED_FILE:Path = Path(get_env_val_safe(EnvFields.ANIME_FILTERED))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)
	anime_filtered, filtered_out = filter_dataset(anime_raw)
	anime_filtered.to_csv(FILTERED_FILE, index=False)

	anime_filtered[DatasetDescriptors.ColumnName]=DatasetDescriptors.Filtered
	anime_raw[DatasetDescriptors.ColumnName]=DatasetDescriptors.Raw
	filter_comparison_frame = pd.concat([ # purely for comparison
		anime_raw.drop( # Cannot compare types which no longer exist.
			index=anime_raw[(anime_raw['type']=='Music')|(anime_raw['type']=='Unknown')].index
		),
		anime_filtered
	],axis=0)
	compare_by_group(filter_comparison_frame, str(RESULTS_FOLDER))
	
	# Stacked barchart counting removed entities
	F01,F01_ax = comparison_barchart_by_type(anime_filtered,filtered_out)
	F01.suptitle('Filter Results')
	F01.savefig('{}/F01_filter_results.tiff'.format(RESULTS_FOLDER))

if __name__ == '__main__':
	generate_graph(True)