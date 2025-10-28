import clean,filter
from __init__ import get_cleaned_anime_dataset, get_dataset, get_filtered_anime_dataset
import pandas as pd
from helpers.context import load_find_env, get_env_val_safe, EnvRequiredFields
from plots import compare_by_group
from pathlib import Path
def generate_graphs(load_env:bool):
	if load_env:
		load_find_env()
	RESULTS_FOLDER:Path = Path(get_env_val_safe(EnvRequiredFields.CF_FOLDER_COMPARE))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)

	anime_raw = get_dataset()
	anime_raw['DATASET_DESCRIPTOR']='Original'
	
	anime_filtered = get_filtered_anime_dataset()
	anime_filtered['DATASET_DESCRIPTOR']='Filtered'
	
	anime_cleaned = get_cleaned_anime_dataset()
	anime_cleaned['DATASET_DESCRIPTOR']='Cleaned'
	
	clean_comparison_frame = pd.concat([
		anime_cleaned,
		anime_filtered
	],axis=0)
	compare_by_group(clean_comparison_frame, str(RESULTS_FOLDER))

if __name__ == '__main__':
	generate_graphs(True)