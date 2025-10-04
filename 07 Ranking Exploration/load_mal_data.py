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

# get dm libs
from typing import List,Tuple
import seaborn as sns;
import matplotlib.pyplot as plt;

import pandas as pd;
from pandas.plotting import scatter_matrix
import numpy as np;

from sklearn import set_config
set_config(transform_output='pandas');
def load_anime()->Tuple[pd.DataFrame,int,int]:
	select_columns:List[str] = [
		'anime_id', 'airing',
	]
	frame:pd.DataFrame = pd.read_csv(data_anime_info, usecols=select_columns)
	total_anime:int = frame.shape[0]
	frame.drop(index=frame[frame['airing']==False].index, inplace=True) # CHANGE TO STATUS==FINISHED AIRING
	total_airing:int = frame.shape[0]
	return (frame,total_airing,total_anime)

anime_frame_data = load_anime()
anime_frame = anime_frame_data[0]
# print(anime_frame.describe())
# print(anime_frame.head())
def load_rankings(anime_frame:pd.DataFrame|None = None, read_nrows:int|None=None)->pd.DataFrame:
	if (data_ranking_info.isspace()):
		raise Exception('user_list is whitespace, cannot load_users')
	select_columns=[
		'anime_id',
		'username',
		'my_watched_episodes',
		'my_score',
		'my_status',
		# 'my_last_updated'
	]
	frame:pd.DataFrame = pd.read_csv(data_ranking_info, usecols=select_columns,nrows=read_nrows)
	# Remove series found in this data.
	if (anime_frame is not None):
		total_rankings:int = frame.shape[0]
		frame.drop(index=frame[frame['anime_id'].isin(anime_frame['anime_id'])].index, inplace=True)
		rankings_left:int = frame.shape[0]
		print('total:', total_rankings)
		print('dropped: ', total_rankings-rankings_left)
		print('left:', rankings_left)
	# Status cannot be greater than  6 or less than 1, some data is.
	frame.drop(index=frame[(frame['my_status']>6) | (frame['my_status']<1)].index,inplace=True)
	anime_eps = get_anime_episodes() # TODO move into load_anime() pipeline... restructure  the previous if to accomodate.
	frame = frame.merge(anime_eps, on='anime_id', how='left')
	frame['ratio_watched'] = frame['my_watched_episodes'] / frame['anime_episodes']
	frame.loc[frame['ratio_watched']>1, 'ratio_watched'] = 1.0
	return frame

def get_anime_episodes()->pd.DataFrame:
	frame =  pd.read_csv(
		filepath_or_buffer=data_anime_info,
		usecols=['anime_id', 'episodes']
	)
	frame.rename(columns={
		'episodes':'anime_episodes'
	},inplace=True)
	return frame

df:pd.DataFrame = load_rankings(anime_frame)
print('loaded rankings')
# print(df.info())
# print (df.head())
print(df.describe())

# tdf = df.drop(columns=['username','my_watched_episodes'])
# group = tdf.groupby(by=['username'])
# users_watched = group.cumsum()
# users_watched.info()
# users_watched.head()
# users_watched.describe()
fig_0705,ax = plt.subplots()
data_by_user = df.groupby(by=['username'])
user_shows_watched = data_by_user['anime_id'].count()
user_shows_watched.rename('shows_watched', inplace=True)

user_avg_rating = data_by_user['my_score'].mean()
user_avg_rating.rename('avg_rating', inplace=True)

user_summary = pd.merge(left=user_avg_rating,right=user_shows_watched, how='left', on='username')
user_summary.info()
user_summary.plot.scatter(x='avg_rating', y='shows_watched')
# Plot Average Rating, by [User, Shows Watched]
exit()

fig_0701,ax = plt.subplots()
df.boxplot(column=['my_score'], ax=ax)
fig_0701.savefig('07 Ranking Exploration/01 boxplot my_score.jpg')

fig_0702,ax = plt.subplots()
df.boxplot(column=['my_watched_episodes'], ax=ax)
fig_0702.savefig('07 Ranking Exploration/02 boxplot my_watched_episodes.jpg')

fig_0703,ax = plt.subplots()
status_counts = df['my_status'].value_counts()
print(status_counts)
status_counts = status_counts.reindex([1,2,3,4,5,6])
print(status_counts)
boxplot = status_counts.plot.bar(rot=0.0, ax=ax)
fig_0703.savefig('07 Ranking Exploration/03 bar plot my_status.jpg')

fig_0704,ax = plt.subplots()
scatplot = df.plot.scatter(x='my_watched_episodes',y='my_score', c='DarkBlue',ax=ax)
fig_0704.savefig('07 Ranking Exploration/04 scatterplot status by score.jpg')

fig_0705,ax = plt.subplots()
score_counts = df['my_status'].value_counts()
print(score_counts)
score_counts = score_counts.reindex([0,1,2,3,4,5,6,7,8,9,10])
print(score_counts)
boxplot = score_counts.plot.bar(rot=0.0, ax=ax)
fig_0705.savefig('07 Ranking Exploration/03 bar plot my_score.jpg')

# fig_0704 = plt.figure()
# df.boxplot(column=['my_score','my_watched_episodes','my_status'])
# plt.savefig('07 Ranking Exploration/04 boxplot multi-variate.jpg')

def ep_quantile(q:float):
	return df['my_watched_episodes'].quantile(q=q)
q3 = ep_quantile(0.75)
q1 = ep_quantile(0.25)
IQR = (q3-q1)*1.5
print('IQR:',IQR)
print('Upper Range:', IQR+q3)