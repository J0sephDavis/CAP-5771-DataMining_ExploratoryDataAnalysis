# # Get Environment Information
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple,List
import matplotlib.ticker as ticker
import numpy as np

import os
from dotenv import load_dotenv, find_dotenv;
de_path = find_dotenv(filename='data.env', raise_error_if_not_found=True)
load_dotenv(de_path, override=True)

mal_data_folder = os.getenv('MAL_DATA_FOLDER','')
print(mal_data_folder)

data_ranking_info = os.getenv('MAL_RANKING_LIST','')
print(data_ranking_info)

data_user_info = os.getenv('MAL_USER_LIST','')
print(data_user_info)

data_anime_info:str = os.getenv('MAL_ANIME_LIST','')
print(data_anime_info)


figures_filter_results = '10 CP1 Data Cleaning/filter_results'
figures_clean_results = '10 CP1 Data Cleaning/clean_results'

DEFAULT_FIGURE_SIZE=(5,5)
DEFAULT_FIGURE_DPI=300
ROWS_TO_READ:int|None = None
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

# # Data Handling Functions
def read_anime_dataset(nrows:int|None = None, use_cols:List[str]|None = ANIME_USE_COLUMNS)->pd.DataFrame:
	""" Load the AnimeList.csv dataset into a dataframe """
	print('nrows=','all' if nrows is None else nrows)
	frame = pd.read_csv(
		filepath_or_buffer=data_anime_info,
		nrows=nrows,
		usecols=use_cols
	)
	return frame

def filter_dataset(anime_list:pd.DataFrame)->Tuple[pd.DataFrame,pd.DataFrame]:
	frame = anime_list.copy()
	""" Apply filtering rules to the AnimeList dataset. Returns the filtered frame & another frame with just the removed records. """
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

def clean_dataset(anime_list:pd.DataFrame)->Tuple[pd.DataFrame,pd.DataFrame]:
	""" Apply cleaning rules to the AnimeList dataset. Return the clean set & the records that were removed. """
	frame = anime_list.copy()
	impossible_score:pd.Series[bool] = (frame['score']<1)|(frame['score']>10)|(frame['score'].isnull())
	no_members:pd.Series[bool] = (frame['members']==0)|(frame['members'].isnull())
	invalid_status:pd.Series[bool] = (frame['status'].isnull())
	no_genre:pd.Series[bool] = (frame['genre'].isnull())
	REMOVE = (impossible_score | no_members | invalid_status | no_genre)
	removed = frame.loc[REMOVE].copy()
	frame.drop(index=REMOVE.index,inplace=True)
	return anime_list, removed

# # Plotting Functions
def barchart_by_type(frame:pd.DataFrame,
		figsize=DEFAULT_FIGURE_SIZE, figure_dpi=DEFAULT_FIGURE_DPI
	)->Tuple[plt.Figure, plt.Axes]:
	""" Plots the amount of entries by the categorical feature 'type'. Returns figure, axes """
	type_counts = frame['type'].value_counts()
	figure,axes = plt.subplots(dpi=figure_dpi)
	type_counts.plot.bar(ax=axes, figsize=figsize)
	axes.set_xlabel('Content Types')
	axes.set_ylabel('Count')
	axes.set_title('Entries by Content Type')
	return figure,axes

def boxplot_by_type(frame:pd.DataFrame,
		column:str, exclude_types:List[str]=[], sub_by:str|None = None,
		plot_overall:bool=False, plot_aggregate:bool=False, plot_all_except_include:bool=False,
		show_fliers:bool=True, show_mean:bool=True,
		figure_dpi:int = 300,
		**matplot_kwargs
	)->Tuple[plt.Figure,plt.Axes]:
	""" Plots the column by type. plot_overall shows the entire dataframes boxplot. plot_aggregate respects exclude_types """
	if not (column in frame.columns):
		raise KeyError('boxplot_by_type {} not found in frame.columns'.format(column))
	
	figure,axes = plt.subplots(dpi=figure_dpi)
	# Set the default figure size to 20in by 20in...
	# Set default width to 0.5 * width of graph (must be set to get them to auto adjust when plotting overall/aggregate)
	matplot_kwargs.setdefault('figsize',DEFAULT_FIGURE_SIZE)
	matplot_kwargs.setdefault('widths',0.5)

	FILTERED_FRAME = (frame[~frame['type'].isin(exclude_types)] if (len(exclude_types) != 0) else frame)
	FILTERED_FRAME.boxplot(
			column=[column],ax=axes,
			by='type' if sub_by is None  else ['type', sub_by],
			showfliers=show_fliers,
			showmeans=show_mean, meanline=show_mean,
			**matplot_kwargs
		)

	labels = [label.get_text() for label in axes.get_xticklabels()]
	def additional_plot(df:pd.DataFrame, label:str):
		df.boxplot(
			column=[column], ax=axes, by = (sub_by if sub_by is not None else None),
			showfliers=show_fliers,
			showmeans=show_mean, meanline=show_mean,
			positions=[len(labels)+1],
			**matplot_kwargs
		)
		labels.append(label)
		axes.set_xticklabels(labels)

	if plot_overall: # Insert the overall boxplot & correct xticklabels
		additional_plot(frame,'All')
	
	if plot_aggregate: # Insert the aggregate (of displayed data), correct xticklabels
		additional_plot(FILTERED_FRAME, 'Aggregate')
	
	if plot_all_except_include and len(exclude_types) != 0:
		additional_plot(frame[frame['type'].isin(exclude_types)],'Excluded')

	title:str = '{} by Content Type'.format(column)
	figure.suptitle('')
	axes.set_title(title)

	# sub_title:str = '({} {})'.format(
	# 	'Show Fliers' if show_fliers else 'Hide Fliers',
	# 	', Show Mean' if show_mean else ''
	# )
	# axes.set_title('')

	axes.set_xlabel('')
	axes.set_ylabel('')
	return figure,axes

def comparison_barchart_by_type(
		filtered_frame:pd.DataFrame,
		removed_frame:pd.DataFrame,
		figure_dpi=DEFAULT_FIGURE_DPI,
		**matplot_kwargs
	)->Tuple[plt.Figure, plt.Axes]:
	""" Stacked barchart showing removed vs remaining records """
	matplot_kwargs.setdefault('figsize',DEFAULT_FIGURE_SIZE)
	leftover = filtered_frame['type'].value_counts()
	print('leftover:')
	print(leftover)
	leftover.name='Leftover'

	removed = removed_frame['type'].value_counts()
	removed.name='Removed'
	print('removed:')
	print(removed)
	total_records = (leftover.sum() + removed.sum())
	total_left = leftover.sum()
	total_removed = removed.sum()
	float_removed = total_removed / total_records
	print('total records: {}'.format(total_records))
	print('total_left: {}'.format(total_left))
	print('total_removed: {}'.format(total_removed))
	print('float_removed: {}'.format(float_removed))
	figure,axes = plt.subplots(dpi=figure_dpi)
	tdf = pd.concat([leftover,removed],axis=1)
	tdf.plot(ax=axes, kind='bar',stacked=True, rot=0, **matplot_kwargs)
	axes.set_xlabel('')
	# axes.set_ylabel('Count')
	return figure,axes

anime_raw = read_anime_dataset(ROWS_TO_READ)
# ------------------------------------------------------------------------------
def compare_by_group(comparison_frame:pd.DataFrame, figure_folder:str):
	rotation=12
	# Compare each type before & after filtering. Score Distributions
	F02A, F02A_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['TV'],
		column='score',
		sub_by='DATASET_DESCRIPTOR',
		rot=rotation
	)
	F02A.savefig('{}/F02A.tiff'.format(figure_folder))
	F02B, F02B_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='score',
		sub_by='DATASET_DESCRIPTOR',
	)
	F02B.savefig('{}/F02B.tiff'.format(figure_folder))

	# Compare each type before & after filtering. Score Distributions
	F03A, F03A_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['TV'],
		column='members',
		sub_by='DATASET_DESCRIPTOR',
		rot=rotation
	)
	F03A.savefig('{}/F03A.tiff'.format(figure_folder))
	F03B, F03B_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='members',
		sub_by='DATASET_DESCRIPTOR',
	)
	F03B.savefig('{}/F03B.tiff'.format(figure_folder))

	# Compare each type before & after filtering. Score Distributions
	F04A, F04A_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['TV'],
		column='members',
		sub_by='DATASET_DESCRIPTOR',
		show_fliers=False,
		rot=rotation
	)
	F04A.savefig('{}/F04A.tiff'.format(figure_folder))
	F04B, F04B_ax = boxplot_by_type(
		clean_comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='members',
		sub_by='DATASET_DESCRIPTOR',
		show_fliers=False,
	)
	F04B.savefig('{}/F04B.tiff'.format(figure_folder))
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# # Data Filtering Results (visualize)
# - 1. Barchart of Types
# - 2. Score by Type
# - 3. Members by Type (Excluding TV)
# - 4. Members by Type (Just TV)
anime_filtered, filtered_out = filter_dataset(anime_raw)

# Stacked barchart counting removed entities
F01,F01_ax = comparison_barchart_by_type(anime_filtered,filtered_out)
# F01.suptitle('Filter Results')
F01.savefig('{}/F01_filter_results.tiff'.format(figures_filter_results))

anime_raw['DATASET_DESCRIPTOR']='Original'
anime_filtered['DATASET_DESCRIPTOR']='Filtered'
clean_comparison_frame = pd.concat([ # purely for comparison
	anime_raw.drop( # Cannot compare types which no longer exist.
		index=anime_raw[(anime_raw['type']=='Music')|(anime_raw['type']=='Unknown')].index
	),
	anime_filtered
],axis=0)
compare_by_group(clean_comparison_frame, figures_filter_results)
del clean_comparison_frame

# ------------------------------------------------------------------------------

# # Data Cleaning

anime_cleaned, cleaned_out = clean_dataset(anime_filtered)
# # Comparison Frame
anime_cleaned['DATASET_DESCRIPTOR']='cleaned'
clean_comparison_frame = pd.concat([
	anime_cleaned,
	anime_filtered
],axis=0)
compare_by_group(clean_comparison_frame, figures_clean_results)
# Stacked barchart counting removed entities
F01,F01_ax = comparison_barchart_by_type(anime_cleaned,cleaned_out)
F01.suptitle('Filter Results')
F01.savefig('{}/F01.tiff'.format(figures_clean_results))
anime_cleaned.drop(columns='DATASET_DESCRIPTOR',inplace=True)
anime_cleaned.to_csv('10 CP1 Data Cleaning/AnimeList_filtered_cleaned.csv', index=False)