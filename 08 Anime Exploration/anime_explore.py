import os
from dotenv import load_dotenv, find_dotenv;
from typing import Tuple,List
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

import pandas as pd

def load_anime(nrows:int|None=None)->pd.DataFrame:
	select_columns:List[str] = [
		'anime_id',
		'episodes',
		'scored_by', 'rank', 'score',
		'popularity', 'members',
		'favorites',
		'title', 'type',
		'status'
	];
	print('nrows=','all' if nrows is None else nrows)
	frame:pd.DataFrame = pd.read_csv(data_anime_info, usecols=select_columns, nrows=nrows)
	
	# Shows must have finished airing.
	frame.drop(index=frame[frame['status']!='Finished Airing'].index, inplace=True)
	# We are only interested in video content recommendations.
	frame.drop(index=frame[frame['type']=='Music'].index,inplace=True)
	
	# Remove columns which are only significant for filtering.
	frame.drop(columns=['status'], inplace=True)
	# Calculate Column	
	frame['fav_per_member'] = frame['favorites'] / frame['members']
	return frame
df = load_anime(1000)
print(df.info())
print()
print(df.describe())
print()
print(df.head(2))
print()

import matplotlib.pyplot as plt;
# Type Analysis (plot for each)
# - BAR PLOT, entries per type
# - BOX PLOT, score distribution
# - Avg score per type
# - AVG MEMBERS per TYPE 
# - favorites/member?


def test_boxplot(frame:pd.DataFrame, column:str):
	if not (column in frame.columns):
		raise KeyError('boxplot_by_type {} not found in frame.columns'.format(column))
	figure,axes = plt.subplots()
	
	frame.boxplot(
		column=[column], by='type',
		ax=axes,
		showfliers=False,
		positions=range(1,len(frame['type'].unique())+1)
	)
	labels = [label.get_text() for label in axes.get_xticklabels()]
	print(labels)
	frame.boxplot(
		column=[column],
		ax=axes,
		showfliers=False,
		positions=[0]
	)
	labels.append('overall')
	axes.set_xticklabels(labels)
	axes.set_xlabel('Content Types')
	axes.set_ylabel(column)
	axes.set_title('{} by Content Type (TEST)'.format(column))
	return figure,axes

test = test_boxplot(df,'members')
f,a = plt.subplots()
df.boxplot(
		column=['members'],
		ax=a,
		showfliers=False,
		positions=[0]
	)
exit()
fig_01,ax = plt.subplots()
df.boxplot(column=['score'], by='type',ax=ax)
fig_01.savefig('08 Anime Exploration/01 Score Distribution by Type.jpg')

# fig_02,ax = plt.subplots()
# type_counts = df['type'].value_counts()
# print(type_counts)
# type_counts.plot.bar(ax=ax)
# fig_02.savefig('08 Anime Exploration/02 Entries by Type.jpg')

fig_03,ax = plt.subplots()
df.boxplot(column=['members'], by='type',ax=ax, showfliers=False,showmeans=True)
fig_03.savefig('08 Anime Exploration/03 Members by Type (sans outliers).jpg')

fig_04,ax = plt.subplots()
df.boxplot(column=['members'], by='type',ax=ax, showfliers=True,showmeans=True)
fig_04.savefig('08 Anime Exploration/04 Members by Type (with outliers).jpg')

fig_05,ax = plt.subplots()
df[(df['type']!='TV')].boxplot(column=['members'], by='type',ax=ax, showfliers=False,showmeans=True)
fig_05.savefig('08 Anime Exploration/05 Members by Type (excluding TV) (without outliers).jpg')

fig_06,ax = plt.subplots()
df[df['members']!=0].boxplot(column=['fav_per_member'], by='type',ax=ax, showfliers=False)
fig_06.savefig('08 Anime Exploration/06 Favorites per Members by Type (without outliers).jpg')

df['member_per_fav'] = df['members'] / df['favorites']
fig_07,ax = plt.subplots()
fig_7_name:str = 'Members per Favorites by Type, No Outliers, Favorites<>0'
df[df['favorites']!=0].boxplot(column=['member_per_fav'], by='type',ax=ax, showfliers=False)
fig_07.savefig('08 Anime Exploration/07 Members per Favorites by Type (without outliers).jpg')


# Non-movie analysis
# - score vs. episodes scatter plot
# - favorites/member?