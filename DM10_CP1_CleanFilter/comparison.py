import clean,filter
import pandas as pd
from helpers.context import load_find_env, get_env_val_safe, EnvFields
from plots import compare_by_group
from pathlib import Path
from AnimeList import (
	dataset as _dataset,
	filter as _filter,
	clean as _clean,
	DatasetDescriptors as _DatasetDescriptors,
)
def generate_graphs(load_env:bool):
	if load_env:
		load_find_env()
	RESULTS_FOLDER:Path = Path(get_env_val_safe(EnvFields.ANIME_CF_FOLDER_COMPARE))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)

	anime_raw = _dataset.get_dataset()
	anime_raw[_DatasetDescriptors.ColumnName]=_DatasetDescriptors.Raw
	
	anime_filtered = _filter.get_dataset()
	anime_filtered[_DatasetDescriptors.ColumnName]=_DatasetDescriptors.Filtered
	
	anime_cleaned = _clean.get_clean_dataset()
	anime_cleaned[_DatasetDescriptors.ColumnName]=_DatasetDescriptors.Cleaned
	
	clean_comparison_frame = pd.concat([
		anime_cleaned,
		anime_filtered
	],axis=0)
	compare_by_group(clean_comparison_frame, str(RESULTS_FOLDER))

if __name__ == '__main__':
	generate_graphs(True)