from AnimeList import (
	filter as _filter,
	clean as _clean,
	DatasetDescriptors as _DatasetDescriptors,
)
from plots import (
	comparison_barchart_by_type as _comparison_barchart_by_type,
	compare_by_group as _compare_by_group
)
from helpers.context import (
	load_find_env as _load_find_env,
	get_env_val_safe as _get_env_val_safe,
	EnvFields as _EnvFields,
)
from pathlib import (
	Path as _Path,
)
import pandas as _pd

def generate_graphs(load_env:bool):
	if load_env:
		_load_find_env()
	anime_filtered = _filter.get_dataset(nrows=None)
	RESULTS_FOLDER:_Path = _Path(_get_env_val_safe(_EnvFields.ANIME_CF_FOLDER_CLEANED))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)
	# Compare results after cleaning
	try: # This is a shitty check because anime_cleaned will run & then cleaned_out will error, just wasting time. Not worth rewriting.
		anime_cleaned = _clean.get_clean_dataset()
		anime_cleaned_out = _clean.get_out_dataset()
	except FileNotFoundError:
		anime_cleaned, anime_cleaned_out = _clean.clean_dataset(anime_filtered)
		anime_cleaned.to_csv(_get_env_val_safe(_EnvFields.ANIME_CLEANED))
		anime_cleaned_out.to_csv(_get_env_val_safe(_EnvFields.ANIME_CLEANED_OUT))
	
	anime_filtered[_DatasetDescriptors .ColumnName]=_DatasetDescriptors .Filtered
	anime_cleaned[_DatasetDescriptors .ColumnName]=_DatasetDescriptors .Cleaned	
	# # Comparison Frame
	clean_comparison_frame = _pd.concat([
		anime_cleaned,
		anime_filtered
	],axis=0)
	_compare_by_group(clean_comparison_frame, str(RESULTS_FOLDER))
	# Stacked barchart counting removed entities
	F01,F01_ax = _comparison_barchart_by_type(anime_cleaned,anime_cleaned_out)
	F01.suptitle('Clean Results')
	F01.savefig('{}/F01.tiff'.format(RESULTS_FOLDER))

if __name__ == '__main__':
	generate_graphs(True)