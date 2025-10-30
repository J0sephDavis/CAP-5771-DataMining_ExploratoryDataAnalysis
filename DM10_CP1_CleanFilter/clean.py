from pathlib import Path
from helpers.context import EnvFields,get_env_val_safe,load_find_env
import os
from typing import Tuple,List, Optional
import matplotlib.pyplot as plt
import pandas as pd
from __init__ import get_filtered_anime_dataset, DatasetDescriptors
from plots import comparison_barchart_by_type, compare_by_group

def clean_dataframe(anime_list:pd.DataFrame)->Tuple[pd.DataFrame,pd.DataFrame]:
	""" Apply cleaning rules to the AnimeList dataset. Return the clean set & the records that were removed. """
	frame = anime_list.copy()
	impossible_score:pd.Series[bool] = (frame['score']<1)|(frame['score']>10)|(frame['score'].isnull())
	no_members:pd.Series[bool] = (frame['members']==0)|(frame['members'].isnull())
	invalid_status:pd.Series[bool] = (frame['status'].isnull())
	no_genre:pd.Series[bool] = (frame['genre'].isnull())
	REMOVE = (impossible_score | no_members | invalid_status | no_genre)
	removed = frame.loc[REMOVE].copy()
	frame.drop(index=removed.index,inplace=True)
	return frame, removed


def generate_graphs(load_env:bool):
	if load_env:
		load_find_env()
	anime_filtered = get_filtered_anime_dataset(None)
	RESULTS_FOLDER:Path = Path(get_env_val_safe(EnvFields.ANIME_CF_FOLDER_CLEANED))
	CLEANED_FILE:Path = Path(get_env_val_safe(EnvFields.ANIME_CLEANED))
	RESULTS_FOLDER.mkdir(mode=0o775, parents=True,exist_ok=True)
	# Compare results after cleaning
	anime_cleaned, cleaned_out = clean_dataframe(anime_filtered)
	anime_cleaned.to_csv(CLEANED_FILE, index=False)
	anime_filtered[DatasetDescriptors.ColumnName]=DatasetDescriptors.Filtered
	anime_cleaned[DatasetDescriptors.ColumnName]=DatasetDescriptors.Cleaned	
	# # Comparison Frame
	clean_comparison_frame = pd.concat([
		anime_cleaned,
		anime_filtered
	],axis=0)
	compare_by_group(clean_comparison_frame, str(RESULTS_FOLDER))
	# Stacked barchart counting removed entities
	F01,F01_ax = comparison_barchart_by_type(anime_cleaned,cleaned_out)
	F01.suptitle('Clean Results')
	F01.savefig('{}/F01.tiff'.format(RESULTS_FOLDER))


if __name__ == '__main__':
	generate_graphs(True)