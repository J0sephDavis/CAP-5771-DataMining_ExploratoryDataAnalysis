import os
from dotenv import load_dotenv, find_dotenv;
from typing import Tuple,List
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple,List
import matplotlib.ticker as ticker
import numpy as np
ROWS_TO_READ:int|None = 1000
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
def get_environment_variables()->Tuple[str,str,str,str]:
	find_dotenv(filename='data.env')
	load_dotenv('data.env')
	mal_data_folder = os.getenv('MAL_DATA_FOLDER','')
	print(mal_data_folder)
	data_ranking_info = os.getenv('MAL_RANKING_LIST','')
	print(data_ranking_info)
	data_user_info = os.getenv('MAL_USER_LIST','')
	print(data_user_info)
	data_anime_info:str = os.getenv('MAL_ANIME_LIST','')
	print(data_anime_info)
	return (mal_data_folder,data_ranking_info,data_user_info,data_anime_info)

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
	# Features
	frame.drop( # Remove the 'status' column. Only used in filtering
		columns=['status'], inplace=True
	)
	return frame, removed_records

anime_raw = read_anime_dataset(ROWS_TO_READ)
print(anime_raw.info())
print(anime_raw.describe())

anime_filtered, filtered_out = filter_dataset(anime_raw)

print('Filtered Info:')
print(anime_filtered.info())
print('describe:')
print(anime_filtered.describe())


print('Removed Info:')
print(filtered_out.info())
print('describe:')
print(filtered_out.describe())

# compare removed
leftover = anime_filtered['type'].value_counts()
removed = filtered_out['type'].value_counts()
fig,ax = plt.subplots()
zero = np.zeros(len(removed.index))
for index in removed.index:
	if index not in leftover.index:
		leftover[index]=0
for index in leftover.index:
	if index not in removed.index:
		removed[index]=0
removed.name='Removed'
leftover.name='Leftover'
tdf = pd.concat([leftover,removed],axis=1)
tdf.plot.bar(stacked=True)


fig,ax = plt.subplots()
anime_filtered['group'] = 'filtered dataset'
anime_raw['group'] = 'original dataset'
tdf = pd.concat([anime_filtered, anime_raw])
tdf.info()
tdf.boxplot(column='score', by=['type','group'])

def boxplot_by_type(frame:pd.DataFrame,
		column:str, exclude_types:List[str]=[],
		plot_overall:bool=False, plot_aggregate:bool=False, plot_all_except_include:bool=False,
		show_fliers:bool=True, show_mean:bool=True,
		figure_dpi:int = 100,
		**matplot_kwargs
	)->Tuple[plt.Figure,plt.Axes]:
	""" Plots the column by type. plot_overall shows the entire dataframes boxplot. plot_aggregate respects exclude_types """
	if not (column in frame.columns):
		raise KeyError('boxplot_by_type {} not found in frame.columns'.format(column))
	# Set the default figure size to 20in by 20in...
	# Set default width to 0.5 * width of graph (must be set to get them to auto adjust when plotting overall/aggregate)
	matplot_kwargs.setdefault('figsize',(20,20))
	matplot_kwargs.setdefault('widths',0.5)

	figure,axes = plt.subplots(dpi=figure_dpi)
	FILTERED_FRAME = (frame[~frame['type'].isin(exclude_types)] if (len(exclude_types) != 0) else frame)
	FILTERED_FRAME.boxplot(
			column=[column], by='type', ax=axes,
			showfliers=show_fliers,
			showmeans=show_mean, meanline=show_mean,
			**matplot_kwargs
		)

	labels = [label.get_text() for label in axes.get_xticklabels()]
	def additional_plot(df:pd.DataFrame, label:str):
		df.boxplot(
			column=[column], ax=axes,
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

	axes.set_xlabel('Content Types')
	axes.set_ylabel(column)
	title:str = '{} by Content Type'.format(
		column
	)
	sub_title:str = '({} {})'.format(
		'Show Fliers' if show_fliers else 'Hide Fliers',
		', Show Mean' if show_mean else ''
	)
	figure.suptitle(title)
	axes.set_title(sub_title)
	return figure,axes
exit()